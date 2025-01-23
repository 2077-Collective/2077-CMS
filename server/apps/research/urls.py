# urls.py
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet, AuthorViewSet, tinymce_upload_image
from .redirects_urls import urlpatterns as redirects_urlpatterns
from .rss import LatestArticlesFeed

# Initialize the DefaultRouter
router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'authors', AuthorViewSet, basename='author')

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=False)),

    # Custom redirect URL old slug to new slug
    *redirects_urlpatterns,
    
    # Include router URLs
    path('api/', include(router.urls)),
    
    # Custom URL for retrieving articles by slug or UUID
    re_path(r'^api/articles/(?P<identifier>[-\w0-9a-fA-F]+)/$', ArticleViewSet.as_view({'get': 'retrieve_by_identifier'}), name='article-detail-by-identifier'), 
   
    # Custom URL for retrieving articles by category
    re_path(r'^api/articles/category/(?P<category_slug>[-\w]+)/$', ArticleViewSet.as_view({'get': 'retrieve_by_category'}), name='article-list-by-category'),
    
    # Custom URL for retrieving all categories (with optional filtering for primary categories)
    re_path(r'^api/categories/$', ArticleViewSet.as_view({'get': 'categories'}), name='article-categories'),
    
    # Upload tinyMCE images to Cloudinary
    path('tinymce/upload/', tinymce_upload_image, name='tinymce_upload'),
    
    # RSS feed
    path('research/rss/', LatestArticlesFeed(), name='rss_feed'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)