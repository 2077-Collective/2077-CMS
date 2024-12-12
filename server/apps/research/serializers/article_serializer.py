from rest_framework import serializers
from django.db import transaction
import logging
from django.core.exceptions import ValidationError as DjangoValidationError
from ..models import Article, Author, Category, RelatedArticle
from .author_serializer import AuthorSerializer
from .category_serializer import CategorySerializer

logger = logging.getLogger(__name__)

class ArticleListSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)
    authors = AuthorSerializer(many=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'slug', 'categories', 'authors']

class RelatedArticleSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='to_article.id', read_only=True)
    title = serializers.CharField(source='to_article.title', read_only=True)
    slug = serializers.CharField(source='to_article.slug', read_only=True)
    thumb = serializers.ImageField(source='to_article.thumb', read_only=True)
    
    class Meta:
        model = RelatedArticle
        fields = ['id', 'title', 'slug', 'thumb']

class ArticleSerializer(serializers.ModelSerializer):
    def _handle_error(self, error, operation_type, context_data):
        """
        Centralized error handling for article operations
        """
        if isinstance(error, DjangoValidationError):
            raise serializers.ValidationError(error.message_dict) from error
        
        logger.error(
            f"Error {operation_type} article",
            extra={**context_data, "error": str(error)},
            exc_info=True
        )
        raise serializers.ValidationError({
            "non_field_errors": [f"Unable to {operation_type} article. Please try again later."]
        }) from error

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except Exception as e:
            self._handle_error(e, "creating", {"validated_data": validated_data})

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except Exception as e:
            self._handle_error(e, "updating", {
                "instance_id": instance.id if instance else None,
                "validated_data": validated_data
            })

class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating articles."""
    authors = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all(), many=True, required=False)
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True, required=False)
    related_article_ids = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.filter(status='ready'),
        many=True,
        required=False,
        write_only=True
    )

    class Meta:
        model = Article
        fields = [
            'title', 'slug', 'categories', 'thumb', 'content', 'summary',
            'acknowledgement', 'status', 'authors', 'scheduled_publish_time',
            'is_sponsored', 'sponsor_color', 'sponsor_text_color', 'related_article_ids'
        ]

    def _handle_error(self, error, operation_type, context_data):
        """
        Centralized error handling for article operations
        """
        if isinstance(error, DjangoValidationError):
            raise serializers.ValidationError(error.message_dict) from error
        
        logger.error(
            f"Error {operation_type} article",
            extra={**context_data, "error": str(error)},
            exc_info=True
        )
        raise serializers.ValidationError({
            "non_field_errors": [f"Unable to {operation_type} article. Please try again later."]
        }) from error

    def validate_related_article_ids(self, value):
        """Validate related articles."""
        if len(value) > 3:
            raise serializers.ValidationError("You can only have a maximum of 3 related articles.")
    
        article_id = self.instance.id if self.instance else None
        if article_id is None:
            request = self.context.get('request')
            if request and hasattr(request, 'data'):
                article_id = request.data.get('id')
    
        if article_id and article_id in [article.id for article in value]:
            raise serializers.ValidationError("An article cannot be related to itself.")
    
        return value

    def _handle_relations(self, article, authors, categories, related_article_ids):
        """
        Handle setting related objects for an article.

        Args:
            article: The Article instance to update
            authors: List of Author instances to associate
            categories: List of Category instances to associate
            related_article_ids: List of Article instances to set as related articles
        
        Raises:
            ValidationError: If related objects can't be found or other errors occur
        """
        try:
            if authors:
                article.authors.set(authors)
            if categories:
                article.categories.set(categories)
            
            if related_article_ids is not None:
                with transaction.atomic():
                    # Delete existing relations first
                    RelatedArticle.objects.filter(from_article=article).delete()
                
                    # Create new relations
                    RelatedArticle.objects.bulk_create([
                        RelatedArticle(from_article=article, to_article=related_article)
                        for related_article in related_article_ids
                    ])
                
        except (Article.DoesNotExist, Author.DoesNotExist, Category.DoesNotExist) as e:
            logger.error(
                "Related object not found",
                extra={
                    "article_id": article.id,
                    "error": str(e)
                },
                exc_info=True
            )
            raise serializers.ValidationError(f"Related object not found: {str(e)}") from e
        
        except Exception as e:
            logger.error(
                "Error handling article relations",
                extra={
                    "article_id": article.id,
                    "authors": [a.id for a in authors] if authors else None,
                    "categories": [c.id for c in categories] if categories else None,
                    "related_articles": [r.id for r in related_article_ids] if related_article_ids else None,
                    "error": str(e)
                },
                exc_info=True
            )
            raise serializers.ValidationError("Error setting related objects") from e

    def create(self, validated_data):
        """Create a new Article instance."""
        authors = validated_data.pop('authors', [])
        categories = validated_data.pop('categories', [])
        related_article_ids = validated_data.pop('related_article_ids', [])

        try:
            request = self.context.get('request')
            if not authors and request and hasattr(request, 'user'):
                user_author = Author.objects.filter(user=request.user).first()
                if user_author:
                    authors = [user_author]

            article = Article.objects.create(**validated_data)
            self._handle_relations(article, authors, categories, related_article_ids)
            return article

        except Exception as e:
            self._handle_error(e, "creating", {"validated_data": validated_data})

    def update(self, instance: Article, validated_data: dict) -> Article:
        """Update an existing article instance."""
        authors = validated_data.pop('authors', [])
        categories = validated_data.pop('categories', [])
        related_article_ids = validated_data.pop('related_article_ids', None)
        
        try:
            instance = super().update(instance, validated_data)
            self._handle_relations(instance, authors, categories, related_article_ids)
            return instance

        except Exception as e:
            self._handle_error(e, "updating", {
                "instance_id": instance.id if instance else None,
                "validated_data": validated_data
            })