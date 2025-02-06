# article_admin.py
from django.contrib import admin
from django import forms
from django.db.models import Q
from apps.research.models import Article, ArticleSlugHistory, Category
from tinymce.widgets import TinyMCE
from .slug_history import current_slug_history
from django.conf import settings
from django.http import JsonResponse
from django.urls import path
from ..services.gpt_service import GPTService
import asyncio

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
        
        # Configure TinyMCE widgets
        self.fields['acknowledgement'].widget = TinyMCE(attrs={
            'cols': 80, 
            'rows': 30, 
            'id': "acknowledgement_richtext_field", 
            'placeholder': "Enter Acknowledgement here"
        })
        self.fields['content'].widget = TinyMCE(attrs={
            'cols': 80, 
            'rows': 30, 
            'id': "content_richtext_field", 
            'placeholder': "Enter Article Content here"
        })
        self.fields['gpt_summary'].widget = TinyMCE(attrs={
            'cols': 80, 
            'rows': 15, 
            'id': "gpt_summary_richtext_field", 
            'placeholder': "GPT-generated summary will appear here"
        })
        self.fields['primary_category'].queryset = Category.objects.all()

class ArticleAdmin(admin.ModelAdmin):
    """Admin interface for the Article model."""
    form = ArticleForm
    
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.gpt_service = GPTService()
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('generate-summary/', self.generate_summary_view, name='generate-summary'),
        ]
        return custom_urls + urls

    async def _generate_summary(self, content: str) -> str:
        system_prompt = (
            "You are a professional summarizer at 2077 Research. Below is an article on Ethereum technical aspects. "
            "Your goal is to produce a summary that is shorter than the original content, yet detailed enough for readers "
            "to fully understand the piece without needing to read the original. Your summary should:\n"
            "- Provide enough depth and detail so the user gets a complete understanding of the core ideas.\n"
            "- Be in HTML format, use <h3> tags for headings if needed. Avoid other heading levels.\n"
            "- Minimize the use of bullet points. If you need to list items, you can, but prefer concise paragraph formatting.\n\n"
        )
        return await self.gpt_service.prompt(system_prompt, content)

    def generate_summary_view(self, request):
        if request.method == 'POST':
            content = request.POST.get('content')
            try:
                gpt_summary = asyncio.run(self._generate_summary(content))
                return JsonResponse({'summary': gpt_summary})
            except Exception as e:
                import logging
                logging.error("An error occurred while generating the summary", exc_info=True)
                return JsonResponse({'error': 'An internal error has occurred!'}, status=500)
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    def current_slug_history(self, obj):
        return current_slug_history(obj)
    current_slug_history.short_description = 'Slug Change History'
    
    fieldsets = [
        ('Article Details', {
            'fields': [
                'title', 'slug', 'authors', 'acknowledgement', 'categories', 'primary_category',
                'thumb', 'content', 'summary', 'gpt_summary', 'status', 'scheduled_publish_time'
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

    class Media:
        css = {
            'all': ('/static/article_admin.css',)
        }
        js = ('/static/article_admin.js',)

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