from django.urls import path
from django.views.generic.base import RedirectView

urlpatterns = [
    path('api/articles/block-stm-vs-sealevel-1/', 
         RedirectView.as_view(url='/api/articles/block-stm_vs_sealevel/', permanent=True)),
    path('api/articles/eips-for-nerds-8-eip-7685/', 
         RedirectView.as_view(url='/api/articles/EIP-7685-General-Purpose-Execution-Requests/', permanent=True)),
    path('api/articles/research/eips-for-nerds-8-eip-7685/', 
         RedirectView.as_view(url='/api/articles/EIP-7685-General-Purpose-Execution-Requests/', permanent=True)),
    path('api/articles/charting-ethereums-account-abstraction-roadmap-1/', 
         RedirectView.as_view(url='/api/articles/charting-ethereums-account-abstraction-roadmap-i-eip-3074-eip-7702/', permanent=True)),
]