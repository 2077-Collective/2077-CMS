from django.contrib import admin
from django import forms
from django.db.models import Q
from apps.research.models import Article, ArticleSlugHistory
from tinymce.widgets import TinyMCE
from .slug_history import current_slug_history

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add filtering for related articles to exclude current article and drafts
        if self.instance.pk:
            self.fields['related_articles'].queryset = Article.objects.filter(
                status='ready'
            ).exclude(
                Q(pk=self.instance.pk) | Q(status='draft')
            ).order_by('-scheduled_publish_time')
        
        self.fields['acknowledgement'].widget = TinyMCE(attrs={'cols': 80, 'rows': 30, 'id': "acknowledgement_richtext_field", 'placeholder': "Enter Acknowledgement here"})
        self.fields['content'].widget = TinyMCE(attrs={'cols': 80, 'rows': 30, 'id': "content_richtext_field", 'placeholder': "Enter Article Content here"})

class ArticleAdmin(admin.ModelAdmin):
    """Admin interface for the Article model."""
    form = ArticleForm
    
    def current_slug_history(self, obj):
        return current_slug_history(obj)
    current_slug_history.short_description = 'Slug Change History'
    
    fieldsets = [
        ('Article Details', {
            'fields': [
                'title', 'slug', 'authors', 'acknowledgement', 'categories', 
                'thumb', 'content', 'summary', 'status', 'scheduled_publish_time'
            ]
        }),
        ('Related Content', {
            'fields': ['related_articles'],
            'description': 'Select up to 3 related articles that will appear at the end of this article'
        }),
        ('Sponsorship Details', {
            'fields': ['is_sponsored', 'sponsor_color', 'sponsor_text_color']
        }),
        ('URL Management', {
            'fields': ('current_slug_history',),
            'classes': ('collapse',),
            'description': 'History of URL changes for this article'
        }),
    ]
    
    list_display = ('title', 'display_authors', 'status', 'views', 'display_categories', 'min_read', 'created_at', 'scheduled_publish_time')
    search_fields = ('title', 'authors__user__username', 'authors__twitter_username', 'content')
    list_per_page = 25
    list_filter = ('authors', 'status', 'categories', 'created_at', 'is_sponsored')
    readonly_fields = ('views', 'current_slug_history',)
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

@admin.register(ArticleSlugHistory)
class ArticleSlugHistoryAdmin(admin.ModelAdmin):
    """Admin interface for the ArticleSlugHistory model."""
    list_display = ('article_title', 'old_slug', 'current_slug', 'created_at')
    list_filter = ('created_at', 'article__title')
    search_fields = ('old_slug', 'article__title')
    readonly_fields = ('article', 'old_slug', 'created_at')

    def article_title(self, obj):
        return obj.article.title
    article_title.short_description = 'Article'

    def current_slug(self, obj):
        return obj.article.slug
    current_slug.short_description = 'Current Slug'

    def has_add_permission(self, request):
        return False  # Prevent manual addition

    def has_delete_permission(self, request, obj=None):
        return False  # Prevent deletion

admin.site.register(Article, ArticleAdmin)