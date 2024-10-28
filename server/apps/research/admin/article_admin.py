from django.contrib import admin
from django import forms
from apps.research.models import Article, Author
from tinymce.widgets import TinyMCE

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['acknowledgement'].widget = TinyMCE(attrs={'cols': 80, 'rows': 30, 'id': "acknowledgement_richtext_field", 'placeholder': f"Enter Acknowledgement here"})
        self.fields['content'].widget = TinyMCE(attrs={'cols': 80, 'rows': 30, 'id': "content_richtext_field", 'placeholder': f"Enter Article Content here"})

class ArticleAdmin(admin.ModelAdmin):
    """Admin interface for the Article model."""
    form = ArticleForm
    fieldsets = [
        ('Article Details', {'fields': ['title', 'slug', 'authors', 'acknowledgement', 'categories', 'thumb', 'content', 'summary', 'status', 'scheduled_publish_time']}),
        ('Sponsorship Details', {'fields': ['is_sponsored', 'sponsor_color', 'sponsor_text_color']}),
    ]
    list_display = ('title', 'display_authors', 'status', 'views', 'display_categories', 'min_read', 'created_at', 'scheduled_publish_time')
    search_fields = ('title', 'authors__user__username', 'authors__twitter_username', 'content')
    list_per_page = 25
    list_filter = ('authors', 'status', 'categories', 'created_at', 'is_sponsored')
    readonly_fields = ('views',)
    list_editable = ('status',)

    def display_authors(self, obj):
        """Return a comma-separated list of authors for the article."""
        return ", ".join(author.user.username for author in obj.authors.all())
    display_authors.short_description = 'Authors'

    def display_categories(self, obj):
        """Return a comma-separated list of categories for the article."""
        return ", ".join(category.name for category in obj.categories.all())
    display_categories.short_description = 'Categories'

    def save_model(self, request, obj, form, change):        
        super().save_model(request, obj, form, change)  

    def has_change_permission(self, request, obj=None):
        """Check if the user has permission to change the article."""
        if request.user.is_superuser:
            return True    
        if not super().has_change_permission(request, obj):
            return False
        if obj is not None and not obj.authors.filter(user=request.user).exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        """Check if the user has permission to delete the article."""
        if request.user.is_superuser:
            return True
        if not super().has_delete_permission(request, obj):
            return False
        if obj is not None and not obj.authors.filter(user=request.user).exists():
            return False
        return True

admin.site.register(Article, ArticleAdmin)