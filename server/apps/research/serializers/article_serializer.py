from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from ..models import Article, Author, Category, RelatedArticle
from .author_serializer import AuthorSerializer
from .category_serializer import CategorySerializer

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
    def create(self, validated_data):
        try:
            # Your existing creation logic here
            return super().create(validated_data)
        except DjangoValidationError as e:
            # Handle validation errors specifically, these are safe to expose
            raise serializers.ValidationError(e.message_dict)
        except Exception as e:
            # Log the detailed error for debugging
            logger.error(
                "Error creating article",
                extra={
                    "validated_data": validated_data,
                    "error": str(e)
                },
                exc_info=True
            )
            # Return a generic error message to the client
            raise serializers.ValidationError({
                "non_field_errors": ["Unable to create article. Please try again later."]
            })

    def update(self, instance, validated_data):
        try:
            # Your existing update logic here
            return super().update(instance, validated_data)
        except DjangoValidationError as e:
            # Handle validation errors specifically
            raise serializers.ValidationError(e.message_dict)
        except Exception as e:
            # Log the detailed error for debugging
            logger.error(
                "Error updating article",
                extra={
                    "instance_id": instance.id if instance else None,
                    "validated_data": validated_data,
                    "error": str(e)
                },
                exc_info=True
            )
            # Return a generic error message to the client
            raise serializers.ValidationError({
                "non_field_errors": ["Unable to update article. Please try again later."]
            })

class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating articles."""
    authors = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all(), many=True, required=False)
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True, required=False)
    related_article_ids = serializers.PrimaryKeyRelatedField(queryset=Article.objects.filter(status='ready'), many=True, required=False, write_only=True)

    class Meta:
        model = Article
        fields = ['title', 'slug', 'categories', 'thumb', 'content', 'summary', 'acknowledgement', 'status', 'authors', 'scheduled_publish_time', 'is_sponsored', 'sponsor_color', 'sponsor_text_color', 'related_article_ids']
    
    def validate_related_article_ids(self, value):
        """Validate related articles."""
        if len(value) > 3:
            raise serializers.ValidationError("You can only have a maximum of 3 related articles.")
    
        # Check for self-reference
        article_id = self.instance.id if self.instance else None
        if article_id is None:  # During creation, we check the request data for article ID
            request = self.context.get('request')
            if request and hasattr(request, 'data'):
                article_id = request.data.get('id')
    
        if article_id and article_id in [article.id for article in value]:
            raise serializers.ValidationError("An article cannot be related to itself.")
    
        return value

    def create(self, validated_data):
        """Create a new Article instance."""
        request = self.context.get('request')
        authors = validated_data.pop('authors', [])
        categories = validated_data.pop('categories', [])
        related_article_ids = validated_data.pop('related_article_ids', [])

        try:
            # Assign default author if none provided
            if not authors and request and hasattr(request, 'user'):
                user_author = Author.objects.filter(user=request.user).first()
                if user_author:
                    authors = [user_author]

            # Create the article instance
            article = Article.objects.create(**validated_data)

            # Associate authors and categories
            if authors:
                article.authors.set(authors)
            if categories:
                article.categories.set(categories)

            # Bulk create related articles
            related_articles = [
                RelatedArticle(from_article=article, to_article=related_article)
                for related_article in related_article_ids
            ]
            RelatedArticle.objects.bulk_create(related_articles)

            return article

        except DjangoValidationError as e:
            # Handle validation errors specifically, these are safe to expose
            raise serializers.ValidationError(e.message_dict)
        except Exception as e:
            # Log the detailed error for debugging
            logger.error(
                "Error creating article",
                extra={
                    "validated_data": validated_data,
                    "error": str(e)
                },
                exc_info=True
            )
            # Return a generic error message to the client
            raise serializers.ValidationError({
                "non_field_errors": ["Unable to create article. Please try again later."]
            })

    def update(self, instance: Article, validated_data: dict) -> Article:
        """Update an existing article instance."""
        authors = validated_data.pop('authors', [])
        categories = validated_data.pop('categories', [])
        related_article_ids = validated_data.pop('related_article_ids', None)
        
        try:
            instance = super().update(instance, validated_data)

            if authors:
                instance.authors.set(authors)
            if categories:
                instance.categories.set(categories)
                
            # Update related articles if provided
            if related_article_ids is not None:
                # Clear existing relations
                RelatedArticle.objects.filter(from_article=instance).delete()
                # Create new relations
                for related_article in related_article_ids:
                    RelatedArticle.objects.create(
                        from_article=instance, to_article=related_article
                    )

            return instance

        except DjangoValidationError as e:
            # Handle validation errors specifically
            raise serializers.ValidationError(e.message_dict)
        except Exception as e:
            # Log the detailed error for debugging
            logger.error(
                "Error updating article",
                extra={
                    "instance_id": instance.id if instance else None,
                    "validated_data": validated_data,
                    "error": str(e)
                },
                exc_info=True
            )
            # Return a generic error message to the client
            raise serializers.ValidationError({
                "non_field_errors": ["Unable to update article. Please try again later."]
            })