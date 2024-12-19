from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet
from .redirects_urls import urlpatterns as redirects_urlpatterns
from .views import tinymce_upload_image

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=False)),  # Redirect root to admin

     # custom redirect URL old slug to new slug
    *redirects_urlpatterns,
    
    path('api/', include(router.urls)),
    
    # Custom URL for retrieving articles by slug or UUID
    re_path(r'^api/articles/(?P<identifier>[-\w0-9a-fA-F]+)/$', ArticleViewSet.as_view({'get': 'retrieve_by_identifier'}), name='article-detail-by-identifier'), 
   
    # Custom URL for retrieving articles by category
    re_path(r'^api/articles/category/(?P<category>[-\w]+)/$', ArticleViewSet.as_view({'get': 'retrieve_by_category'}), name='article-list-by-category'),
    # upload tinyMCE images to cloudinary
    path('tinymce/upload/', tinymce_upload_image, name='tinymce_upload'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
