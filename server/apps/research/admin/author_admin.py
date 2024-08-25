from django.contrib import admin
from apps.research.models import Author

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Admin interface for the Author model."""
    
    fieldsets = [
        ('Author Details', {'fields': ['user', 'bio', 'twitter_username']}),
    ]
    list_display = ('user', 'bio', 'twitter_username')
    list_per_page = 25
    search_fields = ('user__username', 'twitter_username')
    
    def save_model(self, request, obj, form, change):
        """Automatically set the author to the logged-in user when creating a new author."""
        if not change:  # If creating a new author
            obj.user = request.user  
        super().save_model(request, obj, form, change)
