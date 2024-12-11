from django.contrib import admin
from django import forms
from apps.research.models import Article, ArticleSlugHistory
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
        self.fields['acknowledgement'].widget = TinyMCE(attrs={'cols': 80, 'rows': 30, 'id': "acknowledgement_richtext_field", 'placeholder': f"Enter Acknowledgement here"})
        self.fields['content'].widget = TinyMCE(attrs={'cols': 80, 'rows': 30, 'id': "content_richtext_field", 'placeholder': f"Enter Article Content here"})
        self.fields['summary'].widget = TinyMCE(attrs={'cols': 80, 'rows': 30, 'id': "summary_richtext_field", 'placeholder': f"Article summary will be generated here"})

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
            "- Minimize the use of bullet points. If you need to list items, you can, but prefer concise paragraph formatting.\n"
        )
        return await self.gpt_service.prompt(system_prompt, content)

    def generate_summary_view(self, request):
        if request.method == 'POST':
            content = request.POST.get('content')
            try:
                # Run the async function in the sync view
                summary = asyncio.run(self._generate_summary(content))
                return JsonResponse({'summary': summary})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        return JsonResponse({'error': 'Invalid request method'}, status=400)

    def current_slug_history(self, obj):
        return current_slug_history(obj)
    current_slug_history.short_description = 'Slug Change History'
    
    fieldsets = [
        ('Article Details', {'fields': ['title', 'slug', 'authors', 'acknowledgement', 'categories', 'thumb', 'content', 'summary', 'status', 'scheduled_publish_time']}),
        ('Sponsorship Details', {'fields': ['is_sponsored', 'sponsor_color', 'sponsor_text_color']}),
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
    readonly_fields = ('views','current_slug_history',)
    list_editable = ('status',)

    class Media:
        css = {
            'all': ('css/article_admin.css',)
        }
        js = ('js/article_admin.js',)

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