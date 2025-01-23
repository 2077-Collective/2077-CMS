# category.py
from django.db import models
from apps.common.models import BaseModel
from django.utils.text import slugify
from django.db import transaction

class Category(BaseModel):
    """Model for categories."""
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)  # New field to mark primary categories

    class Meta:
        verbose_name_plural = 'Categories'
        
    def save(self, *args, **kwargs):
        with transaction.atomic():
            try:
                if not self.slug:
                    self.slug = self.generate_slug()
                if len(self.slug) > 255:
                    raise ValueError("Generated slug exceeds maximum length")
            except ValueError as e:
                raise ValueError(f"Failed to generate valid slug") from e
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def generate_slug(self):
        if not self.name:
            raise ValueError("Name is required to generate slug")

        base_slug = slugify(self.name)
        slug = base_slug
        num = 1
        with transaction.atomic():
            while (
                Category.objects.select_for_update()
                .filter(slug=slug)
                .exclude(id=self.id)  # Exclude current instance when updating
                .exists()
            ):
                slug = f"{base_slug}-{num}"
                num += 1
        return slug