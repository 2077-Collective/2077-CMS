from rest_framework.decorators import action
from django.db.models import F
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
import uuid
import logging
from django.db import transaction
from rest_framework import serializers
from urllib.parse import quote
from .models import Article, ArticleSlugHistory, Author
from .permissions import ArticleUserWritePermission
from .serializers import ArticleSerializer, ArticleCreateUpdateSerializer, ArticleListSerializer, AuthorSerializer  # Import AuthorSerializer
import cloudinary.uploader
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle

# Set up logging
logger = logging.getLogger(__name__)

class ArticleViewSet(viewsets.ModelViewSet):
    """API endpoint for articles."""
    permission_classes = [ArticleUserWritePermission]
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on request method."""
        if self.action == 'list':
            return ArticleListSerializer
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return ArticleCreateUpdateSerializer
        return ArticleSerializer
    
    def get_serializer_context(self):
        """Add request to the serializer context."""
        return {'request': self.request}

    def get_queryset(self):
        """Retrieve articles that are ready to be published."""
        return Article.objects.filter(status='ready')
    
    def create(self, request, *args, **kwargs):
        """Handle article creation."""
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
        """Handle article update."""
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
    
    # Custom action to retrieve articles by slug or UUID
    @action(detail=False, methods=['get'], url_path=r'(?P<identifier>[-\w0-9a-fA-F]+)')
    def retrieve_by_identifier(self, request, identifier=None):
        """Retrieve an article by slug or UUID,  handling old slugs."""
        try:
            with transaction.atomic():
                if self.is_valid_uuid(identifier):
                    instance = Article.objects.get(pk=identifier)
                else:
                    try:
                        instance = Article.objects.get(slug=identifier)
                    except Article.DoesNotExist:
                        # Check if this is an old slug
                        slug_history = get_object_or_404(ArticleSlugHistory, old_slug=identifier)
                        instance = slug_history.article
                        # Return a redirect response with the new URL
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
    
    # Custom action to retrieve articles by category
    @action(detail=False, methods=['get'], url_path=r'category/(?P<category_slug>[-\w]+)')
    def retrieve_by_category(self, request, category_slug=None):
        """Retrieve article list by category."""
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
        """Check if the value is a valid UUID."""
        try:
            uuid.UUID(value)
            return True
        except ValueError:
            return False

class AuthorViewSet(viewsets.ModelViewSet):
    """API endpoint for authors."""
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [ArticleUserWritePermission]

    @action(detail=True, methods=['get'])
    def articles(self, request, pk=None):
        """Retrieve articles written by a specific author."""
        author = self.get_object()
        articles = Article.objects.filter(author=author).select_related('author').prefetch_related('categories')
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
            # Enhanced file validation
            allowed_types = {'image/jpeg', 'image/png', 'image/gif'}
            if not file.content_type.startswith('image/'):
                raise ValidationError("Only image files are allowed")
            if file.content_type not in allowed_types:
                raise ValidationError(f"Unsupported image type. Allowed types: {', '.join(allowed_types)}")
            if file.size > 5 * 1024 * 1024:
                raise ValidationError("File size too large")
            
            # Sanitize filename
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