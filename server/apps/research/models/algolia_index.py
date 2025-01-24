from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register
import logging

# Import models directly
from .article import Article
from .author import Author
from .category import Category

logger = logging.getLogger(__name__)

def serialize_uuid_fields(instance, data):
    """Helper function to serialize UUID fields in the instance."""
    uuid_fields = [field.name for field in instance._meta.fields if field.get_internal_type() == 'UUIDField']
    for field_name in uuid_fields:
        data[field_name] = str(getattr(instance, field_name))
    return data

@register(Article)
class ArticleIndex(AlgoliaIndex):
    """
    Algolia index configuration for the Article model.
    """
    fields = (
        'id',  # Include the UUID field
        'title',
        'summary',
        'content',
        'slug',
        'status',
        'scheduled_publish_time',
        'thumb',
        'views',
        'is_sponsored',
        'sponsor_color',
        'sponsor_text_color',
        'min_read',
        'table_of_contents',
    )
    settings = {
        'searchableAttributes': ['title', 'summary', 'content'],
        'attributesForFaceting': ['status', 'is_sponsored', 'categories'],
        'customRanking': ['desc(views)', 'desc(scheduled_publish_time)'],
    }
    index_name = 'articles'

    def to_dict(self, instance):
        try:
            data = super().to_dict(instance)
            data = serialize_uuid_fields(instance, data)
            if hasattr(instance, 'authors'):
                data['authors'] = [str(author.id) for author in instance.authors.all()]
            if hasattr(instance, 'categories'):
                data['categories'] = [str(category.id) for category in instance.categories.all()]
            return data
        except Exception as e:
            logger.error(f"Error serializing Article instance {instance}: {e}")
            return {}

@register(Author)
class AuthorIndex(AlgoliaIndex):
    """
    Algolia index configuration for the Author model.
    """
    fields = (
        'id',  # Include the UUID field
        'full_name',
        'bio',
        'twitter_username',
    )
    settings = {
        'searchableAttributes': ['full_name', 'bio'],
        'attributesForFaceting': ['twitter_username'],
    }
    index_name = 'authors'

    def to_dict(self, instance):
        try:
            data = super().to_dict(instance)
            data = serialize_uuid_fields(instance, data)
            return data
        except Exception as e:
            logger.error(f"Error serializing Author instance {instance}: {e}")
            return {}

@register(Category)
class CategoryIndex(AlgoliaIndex):
    """
    Algolia index configuration for the Category model.
    """
    fields = (
        'id',  # Include the UUID field
        'name',
        'slug',
        'is_primary',
    )
    settings = {
        'searchableAttributes': ['name'],
        'attributesForFaceting': ['is_primary'],
    }
    index_name = 'categories'

    def to_dict(self, instance):
        try:
            data = super().to_dict(instance)
            data = serialize_uuid_fields(instance, data)
            return data
        except Exception as e:
            logger.error(f"Error serializing Category instance {instance}: {e}")
            return {}