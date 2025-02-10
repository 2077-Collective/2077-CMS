from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet, AuthorViewSet, tinymce_upload_image
from .redirects_urls import urlpatterns as redirects_urlpatterns
from .rss import LatestArticlesFeed

router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'authors', AuthorViewSet, basename='author')

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    *redirects_urlpatterns,
    path('api/', include(router.urls)),
    path('tinymce/upload/', tinymce_upload_image, name='tinymce_upload'),
    re_path(r'^api/articles/category/(?P<category_slug>[-\w]+)/$', 
            ArticleViewSet.as_view({'get': 'retrieve_by_category'}), 
            name='article-list-by-category'),
    re_path(r'^api/categories/$', 
            ArticleViewSet.as_view({'get': 'categories'}), 
            name='article-categories'),
    path('research/rss/', LatestArticlesFeed(), name='rss_feed'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)