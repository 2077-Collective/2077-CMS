from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from .token import csrf_token_view
from django.conf.urls.i18n import i18n_patterns


urlpatterns = [
                  path('admin/', admin.site.urls),

                  # Custom URLS
                  path('', include('apps.research.urls')),
                  path('api/', include('apps.research.urls')),
                  path('newsletter/', include('apps.newsletter.urls')),
                  path('get-csrf-token/', csrf_token_view, name='csrf_token'),

                  # TinyMCE URL
                  path('tinymce/', include('tinymce.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path('i18n/', include('django.conf.urls.i18n')),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
