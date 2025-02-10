from algoliasearch_django import AlgoliaIndex
from algoliasearch_django.decorators import register
from .article import Article
from .author import Author
from .category import Category
from bs4 import BeautifulSoup

def truncate_text(text, max_chars=8000):
    """Truncate text to stay within Algolia's size limits"""
    if not text:
        return ""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."

@register(Article)
class ArticleIndex(AlgoliaIndex):
    index_queryset = Article.objects.filter(status='ready')

    fields = [
        'title',
        'slug',
        'status',
        'views',
        'is_sponsored',
    ]

    settings = {
        'searchableAttributes': [
            'title',
            'content_excerpt',
            'summary',
        ],
        'attributesToSnippet': [
            'content_excerpt:50',
            'summary:30',
        ],
        'snippetEllipsisText': '...',
        'attributesForFaceting': [
            'status',
            'is_sponsored',
            'categories',
            'authors',
        ]
    }

    def get_raw_record(self, instance):
        record = super().get_raw_record(instance)

        # Convert UUID to string
        record['objectID'] = str(instance.id)

        # Clean and truncate HTML content
        if instance.content:
            soup = BeautifulSoup(instance.content, 'html.parser')
            clean_content = soup.get_text(separator=' ', strip=True)
            record['content_excerpt'] = truncate_text(clean_content, 8000)

        if instance.summary:
            record['summary'] = truncate_text(instance.summary, 1000)

        # Add thumbnail URL
        if instance.thumb:
            record['thumb_url'] = instance.thumb.url

        # Handle datetime fields
        if instance.scheduled_publish_time:
            record['scheduled_publish_time'] = instance.scheduled_publish_time.isoformat()

        if instance.created_at:
            record['created_at'] = instance.created_at.isoformat()

        if instance.updated_at:
            record['updated_at'] = instance.updated_at.isoformat()

        # Handle relationships
        if instance.categories.exists():
            record['categories'] = [
                {
                    'name': category.name, 
                    'slug': category.slug,
                    'id': str(category.id)
                }
                for category in instance.categories.all()
            ]

        if instance.authors.exists():
            record['authors'] = [
                {
                    'name': author.full_name or author.user.get_full_name(),
                    'username': author.user.username,
                    'id': str(author.id)
                }
                for author in instance.authors.all()
            ]

        return record

@register(Category)
class CategoryIndex(AlgoliaIndex):
    fields = [
        'name',
        'slug',
        'is_primary',
    ]

    def get_raw_record(self, instance):
        record = super().get_raw_record(instance)
        record['objectID'] = str(instance.id)

        if instance.created_at:
            record['created_at'] = instance.created_at.isoformat()

        if instance.updated_at:
            record['updated_at'] = instance.updated_at.isoformat()

        return record

    settings = {
        'searchableAttributes': ['name'],
        'attributesForFaceting': ['is_primary']
    }

@register(Author)
class AuthorIndex(AlgoliaIndex):
    fields = [
        'full_name',
        'bio',
        'twitter_username',
    ]

    def get_raw_record(self, instance):
        record = super().get_raw_record(instance)
        record['objectID'] = str(instance.id)

        if instance.bio:
            record['bio'] = truncate_text(instance.bio, 1000)

        if instance.created_at:
            record['created_at'] = instance.created_at.isoformat()

        if instance.updated_at:
            record['updated_at'] = instance.updated_at.isoformat()

        return record

    settings = {
        'searchableAttributes': [
            'full_name',
            'bio'
        ]
    }