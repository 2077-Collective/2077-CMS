from django.db import models
from apps.common.models import BaseModel
from django.utils.text import slugify
from django.db import transaction
from django.core.exceptions import ValidationError

class Category(BaseModel):
    """Model for categories."""
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

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
                .exclude(id=self.id)
                .exists()
            ):
                slug = f"{base_slug}-{num}"
                num += 1
        return slug

    def clean(self):
        if self.parent == self:
            raise ValidationError('A category cannot be its own parent')
        
        parent = self.parent
        while parent is not None:
            if parent == self:
                raise ValidationError('Circular reference detected in category hierarchy')
            parent = parent.parent
        
        if self.is_primary and self.parent is not None:
            raise ValidationError('Primary categories cannot have parent categories')
        
        if not self.is_primary and self.children.filter(is_primary=True).exists():
            raise ValidationError('Non-primary categories cannot have primary category children')