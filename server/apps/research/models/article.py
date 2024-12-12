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


def get_default_thumb():
    return f"{settings.MEDIA_URL}images/2077-Collective.png"


class Article(BaseModel):
    """Model for articles."""

    options = (
        ("draft", "Draft"),
        ("ready", "Ready"),
    )

    title = models.TextField()
    content = HTMLField(blank=True, null=True)
    summary = models.TextField(blank=True)
    acknowledgement = HTMLField(blank=True, null=True)
    authors = models.ManyToManyField(Author, blank=True, related_name="articles")
    slug = models.SlugField(max_length=255, blank=True, db_index=True)
    categories = models.ManyToManyField(Category, blank=True, related_name="articles")
    related_articles = models.ManyToManyField(
        "self",
        blank=True,
        symmetrical=False,
        related_name="referenced_by",
        through="RelatedArticle",
    )
    thumb = models.ImageField(
        upload_to="images/", default=get_default_thumb, blank=True
    )
    views = models.PositiveBigIntegerField(default=0)
    status = models.CharField(
        max_length=10, choices=options, default="draft", db_index=True
    )
    scheduled_publish_time = models.DateTimeField(null=True, blank=True, db_index=True)
    table_of_contents = models.JSONField(default=list, blank=True)
    is_sponsored = models.BooleanField(default=False)
    sponsor_color = models.CharField(max_length=7, default="#FF0420")
    sponsor_text_color = models.CharField(max_length=7, default="#000000")

    objects = models.Manager()
    post_objects = ArticleObjects()

    class Meta:
        ordering = ("-scheduled_publish_time",)

    def get_related_articles(self):
        """
        Get manually selected related articles for this article.
        If none exist, fallback to default frontend logic
        """

        manual_related_articles = self.related_articles.filter(status="ready").order_by(
            "-scheduled_publish_time"
        )[:3]

        if manual_related_articles.exists():
            return manual_related_articles

        # Fallback to last 3 articles in the same category

        category_articles = (
            Article.objects.filter(categories__in=self.categories.all(), status="ready")
            .exclude(id=self.id)
            .order_by("-scheduled_publish_time")
            .distinct()[:3]
        )
        return category_articles

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
        soup = BeautifulSoup(self.content, "html.parser")
        headers = soup.find_all(["h1", "h2", "h3"])

        toc = []
        stack = [{"level": 0, "children": toc}]

        for header in headers:
            level = int(header.name[1])
            title = header.get_text()
            header["id"] = slugify(title)

            while level <= stack[-1]["level"]:
                stack.pop()

            new_item = {"title": title, "id": header["id"], "children": []}

            stack[-1]["children"].append(new_item)
            stack.append({"level": level, "children": new_item["children"]})

        self.table_of_contents = toc
        self.content = str(soup)

    def save(self, *args, **kwargs):
        """Override the save method to generate a unique slug and build table of contents."""
        is_new = self.pk is None
        temp_related_articles = []

        # If this is a new article and there are related articles in the form
        if is_new and hasattr(self, "_temp_related_articles"):
            temp_related_articles = self._temp_related_articles
            delattr(self, "_temp_related_articles")

        if not self.slug or self.title_update():
            self.slug = self.generate_unique_slug()

        """Override the save method to track slug changes."""
        if self.pk:  # If this is an existing article
            try:
                old_instance = Article.objects.get(pk=self.pk)
                # Generate new slug first
                if not self.slug or self.title_update():
                    self.slug = self.generate_unique_slug()

                # Then check if we need to create slug history
                if old_instance.slug and old_instance.slug != self.slug:
                    # Only create history if the slug actually changed and isn't empty
                    with transaction.atomic():
                        ArticleSlugHistory.objects.create(
                            article=self, old_slug=old_instance.slug
                        )
            except Article.DoesNotExist:
                pass

        if self.content:
            self.build_table_of_contents()


        with transaction.atomic():
            super().save(*args, **kwargs)

            # If this was a new article and we had temporary related articles
            if is_new and temp_related_articles:
                for related_article in temp_related_articles:
                    RelatedArticle.objects.create(
                        from_article=self, to_article=related_article
                    )

    def set_temp_related_articles(self, related_articles):
        """
        Store related articles temporarily before the initial save.

        Args:
            related_articles: List of Article instances to be related
        """
        self._temp_related_articles = related_articles

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
        if self.pk:  # Only check if the article exists
            original = Article.objects.filter(pk=self.pk).only("title").first()
            if original:
                return original.title != self.title
        return False

class RelatedArticle(models.Model):
    """Through model for related articles to prevent circular references."""

    from_article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="related_from"
    )
    to_article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="related_to"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("from_article", "to_article")
        constraints = [
            models.CheckConstraint(
                check=~models.Q(from_article=models.F("to_article")),
                name="prevent_self_reference",
            ),
        ]

    def clean(self):
        if not self.from_article.pk:
            return

        # Prevent direct circular references
        if RelatedArticle.objects.filter(
            from_article=self.to_article,
            to_article=self.from_article
        ).exists():
            raise ValidationError("Circular references detected.")

        # Maximum of 3 related articles (only check for new records)
        if not self.pk and RelatedArticle.objects.filter(
            from_article=self.from_article
        ).count() >= 3:
            raise ValidationError("Maximum of 3 related articles allowed.")

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.from_article.pk:
                # Lock all related records for this from_article
                locked_relations = RelatedArticle.objects.select_for_update().filter(
                    from_article=self.from_article
                )
                # Force evaluation of the queryset to acquire the lock
                list(locked_relations)

            self.clean()
            super().save(*args, **kwargs)

class ArticleSlugHistory(models.Model):
    """Model to track historical slugs for articles."""

    id = models.AutoField(primary_key=True)
    article = models.ForeignKey(
        "Article", on_delete=models.CASCADE, related_name="slug_history"
    )
    old_slug = models.SlugField(max_length=255, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("article", "old_slug")
        indexes = [
            models.Index(fields=["old_slug"]),
        ]
        db_table = "research_articleslughistory"  # explicitly set table name

    def __str__(self):
        return f"{self.old_slug} -> {self.article.slug}"