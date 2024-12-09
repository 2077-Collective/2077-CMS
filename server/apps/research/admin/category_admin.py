from django.contrib import admin
from apps.research.models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin interface for the Category model."""
    
    list_display = ('name', 'slug', 'created_at')
    list_per_page = 25
    search_fields = ('name',)
    list_filter = ('created_at',)
    ordering = ('name',)
    readonly_fields = ('slug',)
