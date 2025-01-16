from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from .token import csrf_token_view


urlpatterns = [
                  path('admin/', admin.site.urls),

                  # Custom URLS
                  path('', include('apps.research.urls')),
                  path('api/', include('apps.research.urls')),
                  path('newsletter/', include('apps.newsletter.urls')),
                  path('get-csrf-token/', csrf_token_view, name='csrf_token'),

                  # TinyMCE URL
                  path('tinymce/', include('tinymce.urls')),
                  
                  # Django i18n URLs for language switching
                  path('i18n/', include('django.conf.urls.i18n')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
