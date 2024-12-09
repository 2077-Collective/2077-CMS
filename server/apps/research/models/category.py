from django.db import models
from apps.common.models import BaseModel
from django.utils.text import slugify

class Category(BaseModel):
    """Model for categories."""
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.generate_slug()
        self.generate_slug()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def generate_slug(self):

        base_slug = slugify(self.name)
        slug = base_slug
        num = 1
        while Category.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{num}"
            num += 1
        return slug