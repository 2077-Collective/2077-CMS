from django.conf import settings

def tinymce_api_key(request):
    return {'TINYMCE_API_KEY': settings.TINYMCE_API_KEY}