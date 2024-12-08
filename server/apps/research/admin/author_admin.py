from django.contrib import admin
from apps.research.models import Author

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Admin interface for the Author model."""
    
    fieldsets = [
        ('Author Details', {'fields': ['user', 'full_name', 'bio', 'twitter_username']}),
    ]
    list_display = ('user', 'full_name', 'bio', 'twitter_username')
    list_per_page = 25
    search_fields = ('user__username', 'twitter_username')
    
    def save_model(self, request, obj, form, change):
        """Save the model instance to the database."""
        super().save_model(request, obj, form, change)
