# category_serializer.py
from rest_framework import serializers
from ..models import Category

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for the Category model."""
    slug = serializers.SlugField(read_only=True, max_length=255, help_text='URL-friendly version of the category name.')
    is_primary = serializers.BooleanField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'is_primary']