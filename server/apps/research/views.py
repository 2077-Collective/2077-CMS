import logging
from django.views.generic.base import RedirectView
from rest_framework.decorators import action
from django.db.models import F, Count, Q
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
import uuid
from django.db import transaction
from rest_framework import serializers
from urllib.parse import quote
from .models import Article, ArticleSlugHistory, Author, Category
from .permissions import ArticleUserWritePermission
from .serializers import ArticleSerializer, ArticleCreateUpdateSerializer, ArticleListSerializer, AuthorSerializer, CategorySerializer
import cloudinary.uploader
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from django.core.cache import cache
from rest_framework.pagination import PageNumberPagination

# Set up logging
logger = logging.getLogger(__name__)

class CategoryArticlesPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class LoggingRedirectView(RedirectView):
    def get(self, request, *args, **kwargs):
        logger.info(
            f"Redirect request: path={request.path} "
            f"target={self.url} "
            f"user_agent={request.META.get('HTTP_USER_AGENT', 'N/A')}"
        )
        return super().get(request, *args, **kwargs)

class ArticleViewSet(viewsets.ModelViewSet):
    permission_classes = [ArticleUserWritePermission]
    pagination_class = CategoryArticlesPagination
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return ArticleCreateUpdateSerializer
        return ArticleSerializer
    
    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        return Article.objects.filter(status='ready')
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)            
            self.perform_create(serializer)            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Unexpected error during article creation: {e}")
            if isinstance(e, serializers.ValidationError):
                return Response({'error': 'Invalid data provided'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'error': 'Failed to create a new Article'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:                 
            logger.error(f"Unexpected error during article update: {e}")
            if isinstance(e, serializers.ValidationError):
                return Response({'error': 'Invalid data provided'}, status=status.HTTP_400_BAD_REQUEST)       
            return Response({'error': 'Error updating article'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path=r'(?P<identifier>[-\w0-9a-fA-F]+)')
    def retrieve_by_identifier(self, request, identifier=None):
        try:
            with transaction.atomic():
                if self.is_valid_uuid(identifier):
                    instance = Article.objects.get(pk=identifier)
                else:
                    try:
                        instance = Article.objects.get(slug=identifier)
                    except Article.DoesNotExist:
                        slug_history = get_object_or_404(ArticleSlugHistory, old_slug=identifier)
                        instance = slug_history.article
                        new_url = request.build_absolute_uri().replace(
                            f'/api/articles/{quote(identifier)}/',
                            f'/api/articles/{quote(instance.slug)}/'
                        )
                        return Response({
                            'type': 'redirect',
                            'new_url': new_url,
                            'data': self.get_serializer(instance).data
                        }, status=status.HTTP_301_MOVED_PERMANENTLY)
                    
                instance.views = F('views') + 1
                instance.save(update_fields=['views'])
                instance.refresh_from_db(fields=['views'])
                serializer = self.get_serializer(instance)
                return Response({'success': True, 'data': serializer.data})
            
        except Exception as e:
            logger.error(f"Error retrieving article by identifier: {e}")
            return Response({'error': 'Article does not exist'}, 
                          status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'], url_path=r'category/(?P<category_slug>[-\w]+)')
    def retrieve_by_category(self, request, category_slug=None):
        try:
            instances = Article.objects.filter(categories__slug=category_slug)
            if not instances.exists():
                return Response({'error': 'No articles found for this category'}, status=status.HTTP_404_NOT_FOUND)
            serializer = self.get_serializer(instances, many=True)
            return Response({'success': True, 'data': serializer.data})
        except Exception as e:
            logger.error(f"Error retrieving articles by category: {e}")
            return Response({'error': 'Category does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    def is_valid_uuid(self, value):
        try:
            uuid.UUID(value)
            return True
        except ValueError:
            return False
        
    @action(detail=False, methods=['get'], url_path=r'primary-category/(?P<category_slug>[-\w]+)')
    def retrieve_by_primary_category(self, request, category_slug=None):
        try:
            category = get_object_or_404(Category, slug=category_slug, is_primary=True)
            instances = Article.objects.filter(categories=category, status='ready')
            
            page = self.paginate_queryset(instances)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(instances, many=True)
            return Response({'success': True, 'data': serializer.data})
        
        except Category.DoesNotExist:
            logger.error(f"Primary category with slug '{category_slug}' does not exist")
            return Response(
                {'error': f'Primary category with slug "{category_slug}" does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error retrieving articles by primary category: {e}")
            return Response(
                {'error': 'An error occurred while fetching articles'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """Get categories with paginated articles"""
        try:
            articles_page_size = request.query_params.get('articles_page_size', 10)
            try:
                articles_page_size = min(int(articles_page_size), 100)
            except ValueError:
                articles_page_size = 10
            # Query params
            primary_only = request.query_params.get('primary_only', 'false').lower() == 'true'
            sort_by = request.query_params.get('sort_by', 'name')
            articles_page_size = min(int(request.query_params.get('articles_page_size', 10)), 100)

            # Validate sort field
            valid_sort_fields = ['name', 'is_primary', 'article_count']
            if sort_by not in valid_sort_fields:
                return Response({
                    'success': False,
                    'error': f"Invalid sort field. Valid options: {', '.join(valid_sort_fields)}"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get all categories with their article counts
            categories = Category.objects.annotate(
                article_count=Count(
                    'articles',
                    filter=Q(articles__status='ready'),
                    distinct=True
                )
            )

            if primary_only:
                categories = categories.filter(is_primary=True)
            
            categories = categories.order_by(sort_by)
            serializer = CategorySerializer(categories, many=True)

            # Fetch all ready articles with their relationships
            articles = Article.objects.filter(
                status='ready'
            ).select_related(
                'primary_category'
            ).prefetch_related(
                'categories',
                'authors'
            ).order_by('-created_at')

            # Group articles by category
            articles_by_category = {}
            for article in articles:
                for category in article.categories.all():
                    category_id = str(category.id)
                    if category_id not in articles_by_category:
                        articles_by_category[category_id] = []
                    articles_by_category[category_id].append(article)

            logger.debug(f"Total categories with articles: {len(articles_by_category)}")
            logger.debug(f"Total articles fetched: {articles.count()}")

            response_data = []
            for category_data in serializer.data:
                category_articles = articles_by_category.get(category_data['id'], [])
                
                if category_articles:
                    category_data['articles'] = ArticleListSerializer(
                        category_articles[:articles_page_size],
                        many=True,
                        context={'request': request}
                    ).data
                    category_data['total_articles'] = len(category_articles)
                    
                    if category_data['is_primary']:
                        category_data['latest_article'] = ArticleSerializer(
                            category_articles[0],
                            context={'request': request}
                        ).data
                else:
                    category_data['articles'] = []
                    category_data['total_articles'] = 0
                    category_data['latest_article'] = None

                response_data.append(category_data)

            return Response({
                'success': True,
                'data': response_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error retrieving categories: {str(e)}", exc_info=True)
            return Response(
                {'success': False, 'error': 'An error occurred while fetching categories'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [ArticleUserWritePermission]

    @action(detail=True, methods=['get'])
    def articles(self, request, pk=None):
        author = self.get_object()
        articles = Article.objects.filter(authors=author).prefetch_related('categories', 'authors')
        serializer = ArticleSerializer(articles, many=True)
        return Response(serializer.data)

class ImageUploadRateThrottle(UserRateThrottle):
    rate = '60/hour'
    
@require_http_methods(["POST"])
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([ImageUploadRateThrottle])
def tinymce_upload_image(request):
    if request.method == "POST" and request.FILES:
        try:
            file = request.FILES['file']
            allowed_types = {'image/jpeg', 'image/png', 'image/gif'}
            if not file.content_type.startswith('image/'):
                raise ValidationError("Only image files are allowed")
            if file.content_type not in allowed_types:
                raise ValidationError(f"Unsupported image type. Allowed types: {', '.join(allowed_types)}")
            if file.size > 5 * 1024 * 1024:
                raise ValidationError("File size too large")
            
            import re
            safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '', file.name)
            
            upload_data = cloudinary.uploader.upload(
                file,
                folder='article_content',
                allowed_formats=['png', 'jpg', 'jpeg', 'gif'],
                resource_type="image",
                filename_override=safe_filename,
                unique_filename=True
            )
            return JsonResponse({
                'location': upload_data['secure_url']
            })
        except Exception as e:
            logger.error(f"Error uploading image: {str(e)}")
            return JsonResponse(
                {'error': 'An error occurred while uploading the image'}, 
                status=500
            )
    return JsonResponse({'error': 'Invalid request'}, status=400)