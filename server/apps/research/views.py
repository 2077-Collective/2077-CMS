from rest_framework.decorators import action
from django.db.models import F
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.response import Response
import uuid

from .models import Article
from .permissions import ArticleUserWritePermission
from .serializers import ArticleSerializer, ArticleCreateUpdateSerializer

def index(request):
    return render(request, 'index.html')

class ArticleViewSet(viewsets.ModelViewSet):
    """API endpoint for articles."""
    permission_classes = [ArticleUserWritePermission]
    #serializer_class = ArticleSerializer
    
    def get_serializer_class(self):
        """Return appropriate serializer class based on request method."""
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return ArticleCreateUpdateSerializer
        return ArticleSerializer
    
    def get_serializer_context(self):
        """Add request to the serializer context."""
        return {'request': self.request}

    def get_queryset(self):
        """Retrieve articles that are ready to be published."""
        return Article.objects.filter(status='ready')

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
            return Response({'Error': 'Article does not exist'}, status=status.HTTP_404_NOT_FOUND)

        instance.views = F('views') + 1
        instance.save(update_fields=['views'])
        instance.refresh_from_db(fields=['views'])
        serializer = self.get_serializer(instance)
        return Response({'success': True, 'data': serializer.data})
    
    #Custom action to retrieve articles by category
    @action(detail=False, methods=['get'], url_path=r'category/(?P<category>[-\w]+)')
    def retrieve_by_category(self, request, category=None):
        """Retrieve article list by category"""
        instances = Article.objects.filter(categories__name=category)
        serializer = self.get_serializer(instances, many=True)
        return Response({'success': True, 'data': serializer.data})

    
    def is_valid_uuid(self, value):
        """Check if the value is a valid UUID."""
        try:
            uuid.UUID(value)
            return True
        except ValueError:
            return False
