from rest_framework.decorators import action
from django.db.models import F
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
import uuid
import logging

from .models import Article
from .permissions import ArticleUserWritePermission
from .serializers import ArticleSerializer, ArticleCreateUpdateSerializer, ArticleListSerializer

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
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # Custom action to retrieve articles by slug or UUID
    @action(detail=False, methods=['get'], url_path=r'(?P<identifier>[-\w0-9a-fA-F]+)')
    def retrieve_by_identifier(self, request, identifier=None):
        """Retrieve an article by slug or UUID."""
        try:
            if self.is_valid_uuid(identifier):                
                instance = Article.objects.get(pk=identifier)
            else:                
                instance = Article.objects.get(slug=identifier)
        except Article.DoesNotExist:
            return Response({'error': 'Article does not exist'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error retrieving article by identifier: {e}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        instance.views = F('views') + 1
        instance.save(update_fields=['views'])
        instance.refresh_from_db(fields=['views'])
        serializer = self.get_serializer(instance)
        return Response({'success': True, 'data': serializer.data})
    
    # Custom action to retrieve articles by category
    @action(detail=False, methods=['get'], url_path=r'category/(?P<category_slug>[-\w]+)')
    def retrieve_by_category(self, request, category_slug=None):
        """Retrieve article list by category slug."""
        try:
            instances = Article.objects.filter(categories__slug=category_slug)
            if not instances.exists():
                return Response({'error': 'No articles found for this category'}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = self.get_serializer(instances, many=True)
            return Response({'success': True, 'data': serializer.data})
        except Exception as e:
            logger.error(f"Error retrieving articles by category slug: {e}")
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def is_valid_uuid(self, value):
        """Check if the value is a valid UUID."""
        try:
            uuid.UUID(value)
            return True
        except ValueError:
            return False
