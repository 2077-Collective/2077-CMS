from django.db import models
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from apps.common.models import BaseModel
from apps.research.managers import ArticleObjects
from .category import Category
from .author import Author
from django.utils import timezone
from django.conf import settings
from tinymce.models import HTMLField
import json
from bs4 import BeautifulSoup
import uuid
from django.db import transaction
from cloudinary.models import CloudinaryField
import logging

logger = logging.getLogger(__name__)

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
    authors = models.ManyToManyField(Author, blank=True, related_name='articles')
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
        if self.related_articles.count() > 3:
            raise ValidationError({'related_articles': 'You can select up to 3 related articles only.'})

    def calculate_min_read(self):
        if not self.content:
            return 1
        word_count = len(self.content.split())
        words_per_minute = 300
        minutes = max(1, round(word_count / words_per_minute))
        return minutes

    min_read = property(calculate_min_read)

    def __str__(self):
        return self.title

    def build_table_of_contents(self):
        """Build the table of contents from the article content."""
        try:
            if not self.content:
                self.table_of_contents = []
                return

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
        except Exception as e:
            logger.error(f"Error building table of contents: {str(e)}", exc_info=True)
            self.table_of_contents = []

    def get_related_articles(self):
        """
        Returns manually selected related articles if they exist,
        otherwise falls back to automatic recommendations
        """
        try:
            manual_related = self.related_articles.filter(status='ready').order_by('-scheduled_publish_time')[:3]
            
            if manual_related.exists():
                return manual_related
                
            return Article.objects.filter(
                status='ready',
                categories__in=self.categories.all()
            ).exclude(
                id=self.id
            ).distinct().order_by('-scheduled_publish_time')[:3]
        except Exception as e:
            logger.error(f"Error getting related articles: {str(e)}", exc_info=True)
            return Article.objects.none()

    def _ensure_primary_category(self):
        """Ensure that the article has a primary category."""
        try:
            if not self.categories.exists():
                return

            if not self.primary_category:
                self.primary_category = self.categories.first()
        except Exception as e:
            logger.error(f"Error ensuring primary category: {str(e)}", exc_info=True)

    def title_update(self):
        """Check if the title has changed."""
        if not self.pk:
            return True
        try:
            original = Article.objects.get(pk=self.pk)
            return original.title != self.title
        except Article.DoesNotExist:
            return True
        except Exception as e:
            logger.error(f"Error checking title update: {str(e)}", exc_info=True)
            return False

    def _handle_slug(self):
        """Handle slug generation and history."""
        try:
            needs_new_slug = not self.slug or self.title_update()
            
            if needs_new_slug:
                new_slug = self.generate_unique_slug()
                
                if self.pk:
                    try:
                        with transaction.atomic():
                            old_instance = Article.objects.get(pk=self.pk)
                            old_slug = old_instance.slug
                            
                            if (old_slug and old_slug != new_slug and 
                                not ArticleSlugHistory.objects.filter(
                                    article=self,
                                    old_slug=old_slug
                                ).exists()):
                                ArticleSlugHistory.objects.create(
                                    article=self,
                                    old_slug=old_slug
                                )
                    except Article.DoesNotExist:
                        pass
                
                self.slug = new_slug
                
        except Exception as e:
            logger.error(f"Error handling slug: {str(e)}", exc_info=True)
            raise

    def _build_table_of_contents(self):
        """Build the table of contents if content exists."""
        if self.content:
            self.build_table_of_contents()

    def _handle_scheduled_publish(self):
        """Handle scheduled publish logic."""
        try:
            if self.scheduled_publish_time and self.status == 'draft' and timezone.now() >= self.scheduled_publish_time:
                self.status = 'ready'
        except Exception as e:
            logger.error(f"Error handling scheduled publish: {str(e)}", exc_info=True)

    def _validate_thumbnail(self):
        """Validate the thumbnail."""
        try:
            if self.thumb and hasattr(self.thumb, 'public_id'):
                if not self.thumb.public_id:
                    raise ValidationError("Failed to upload image to Cloudinary")
        except Exception as e:
            logger.error(f"Error validating thumbnail: {str(e)}", exc_info=True)
            raise ValidationError(f"Image upload failed: {str(e)}") from e

    def save(self, *args, **kwargs):
        """Override the save method to generate a unique slug, build table of contents, and set primary category."""
        try:
            logger.info(f"Starting save for article {self.pk} with title {self.title}")
            
            self._ensure_primary_category()
            logger.info("Primary category ensured")
            
            self._handle_slug()
            logger.info(f"Slug handled: {self.slug}")
            
            self._build_table_of_contents()
            logger.info("Table of contents built")
            
            self._handle_scheduled_publish()
            logger.info(f"Scheduled publish handled: {self.status}")
            
            self._validate_thumbnail()
            logger.info("Thumbnail validated")

            super().save(*args, **kwargs)
            logger.info("Save completed successfully")
            
        except Exception as e:
            logger.error(f"Error saving article: {str(e)}", exc_info=True)
            raise

    def generate_unique_slug(self):
        """Generate a unique slug for the article."""
        try:
            base_slug = slugify(self.title)
            if not base_slug:
                base_slug = str(uuid.uuid4())[:8]
            
            slug = base_slug
            num = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            return slug
        except Exception as e:
            logger.error(f"Error generating unique slug: {str(e)}", exc_info=True)
            raise

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