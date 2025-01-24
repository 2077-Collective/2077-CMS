# article.py
from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from apps.common.models import BaseModel
from apps.research.managers import ArticleObjects
from .category import Category
from django.utils import timezone
from django.conf import settings
from tinymce.models import HTMLField
import json
from bs4 import BeautifulSoup
import uuid
from django.db import transaction
from cloudinary.models import CloudinaryField

def get_default_thumb():
    return "v1734517759/v4_article_cover_slashing_hhf6tz"

class Article(BaseModel):
    """Model for articles."""
    
    options = (
        ('draft', 'Draft'),
        ('ready', 'Ready'),
    )

    title = models.TextField()
    content = HTMLField(blank=True, null=True)
    summary = models.TextField(blank=True)
    gpt_summary = HTMLField(blank=True, null=True)
    acknowledgement = HTMLField(blank=True, null=True)
    authors = models.ManyToManyField('Author', blank=True, related_name='articles')  # Use string reference
    slug = models.SlugField(max_length=255, blank=True, db_index=True)
    categories = models.ManyToManyField(Category, blank=True, related_name='articles')
    primary_category = models.ForeignKey(
        Category,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='primary_for_articles'
    )
    thumb = CloudinaryField('image', folder='coverImage', default=get_default_thumb, blank=True)
    views = models.PositiveBigIntegerField(default=0)
    status = models.CharField(max_length=10, choices=options, default='draft', db_index=True)    
    scheduled_publish_time = models.DateTimeField(null=True, blank=True, db_index=True)    
    table_of_contents = models.JSONField(default=list, blank=True)
    is_sponsored = models.BooleanField(default=False)
    sponsor_color = models.CharField(max_length=7, default="#FF0420")
    sponsor_text_color = models.CharField(max_length=7, default="#000000")
    related_articles = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='referenced_by',
        verbose_name='Related Articles',
        help_text='Select up to 3 related articles'
    )

    objects = models.Manager()
    post_objects = ArticleObjects()

    class Meta:
        ordering = ('-scheduled_publish_time',)
    
    def clean(self):
        super().clean()
        # Ensure no more than 3 related articles are selected
        if self.related_articles.count() > 3:
            raise ValidationError({'related_articles': 'You can select up to 3 related articles only.'})

    def calculate_min_read(self):
        word_count = len(self.content.split())
        words_per_minute = 300  # Average reading speed (words per minute)
        minutes = max(1, round(word_count / words_per_minute))
        return minutes

    min_read = property(calculate_min_read)

    def __str__(self):
        return self.title

    def build_table_of_contents(self):
        """Build the table of contents from the article content."""
        soup = BeautifulSoup(self.content, 'html.parser')
        headers = soup.find_all(['h1', 'h2', 'h3'])
        
        toc = []
        stack = [{'level': 0, 'children': toc}]

        for header in headers:
            level = int(header.name[1])
            title = header.get_text()
            header['id'] = slugify(title)

            while level <= stack[-1]['level']:
                stack.pop()

            new_item = {'title': title, 'id': header['id'], 'children': []}
            
            stack[-1]['children'].append(new_item)
            stack.append({'level': level, 'children': new_item['children']})

        self.table_of_contents = toc
        self.content = str(soup)

    def get_related_articles(self):
        """
        Returns manually selected related articles if they exist,
        otherwise falls back to automatic recommendations
        """
        manual_related = self.related_articles.filter(status='ready').order_by('-scheduled_publish_time')[:3]
        
        if manual_related.exists():
            return manual_related
            
        # Fallback logic - articles with matching categories
        return Article.objects.filter(
            status='ready',
            categories__in=self.categories.all()
        ).exclude(
            id=self.id
        ).distinct().order_by('-scheduled_publish_time')[:3]

    def _ensure_primary_category(self):
        """Ensure that the article has a primary category."""
        if not self.categories.exists():
            return

        # If no primary category is set, assign the first category as primary
        if not self.primary_category:
            self.primary_category = self.categories.first()

    def _handle_slug(self):
        """Handle slug generation and history."""
        if not self.slug or self.title_update():
            self.slug = self.generate_unique_slug()
        if self.pk:
            try:
                old_instance = Article.objects.get(pk=self.pk)
                if old_instance.slug and old_instance.slug != self.slug:
                    with transaction.atomic():
                        ArticleSlugHistory.objects.create(
                            article=self,
                            old_slug=old_instance.slug
                        )
            except Article.DoesNotExist:
                pass

    def _build_table_of_contents(self):
        """Build the table of contents if content exists."""
        if self.content:
            self.build_table_of_contents()

    def _handle_scheduled_publish(self):
        """Handle scheduled publish logic."""
        if self.scheduled_publish_time and self.status == 'draft' and timezone.now() >= self.scheduled_publish_time:
            self.status = 'ready'

    def _validate_thumbnail(self):
        """Validate the thumbnail."""
        if self.thumb and hasattr(self.thumb, 'public_id'):
            try:
                if not self.thumb.public_id:
                    raise ValidationError("Failed to upload image to Cloudinary")
            except Exception as e:
                raise ValidationError(f"Image upload failed: {str(e)}") from e

    def save(self, *args, **kwargs):
        """Override the save method to generate a unique slug, build table of contents, and set primary category."""
        self._ensure_primary_category()
        self._handle_slug()
        self._build_table_of_contents()
        self._handle_scheduled_publish()
        self._validate_thumbnail()

        super().save(*args, **kwargs)

    def generate_unique_slug(self):
        """Generate a unique slug for the article."""
        base_slug = slugify(self.title)
        slug = base_slug
        num = 1
        while Article.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{num}"
            num += 1
        return slug
    
    def title_update(self):
        """Check if the title has changed."""
        if self.pk:
            original = Article.objects.filter(pk=self.pk).only('title').first()
            if original:
                return original.title != self.title
        return False

class ArticleSlugHistory(models.Model):
    """Model to track historical slugs for articles."""
    id = models.AutoField(primary_key=True)
    article = models.ForeignKey('Article', on_delete=models.CASCADE, related_name='slug_history')
    old_slug = models.SlugField(max_length=255, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('article', 'old_slug')
        indexes = [
            models.Index(fields=['old_slug']),
        ]
        db_table = 'research_articleslughistory'

    def __str__(self):
        return f"{self.old_slug} -> {self.article.slug}"