# article_serializer.py
import logging
from rest_framework import serializers
from ..models import Article, Author, Category
from .author_serializer import AuthorSerializer
from .category_serializer import CategorySerializer
from django.conf import settings

def get_cloudinary_url(resource):
    """
    Handles both legacy images and new optimized images.
    Legacy images: Add optimization parameters
    New images: Will already have optimization from CloudinaryField config
    """
    if not resource:
        return None
    
    public_id = resource.public_id if hasattr(resource, 'public_id') else resource
    try:
        image_id = public_id.split('/')[-1]
        if not image_id:
            raise ValueError("Invalid public_id format")
    except (AttributeError, IndexError) as e:
        logging.error(f"Error processing public_id {public_id}: {str(e)}")
        return None
    base_url = f"{settings.CLOUDINARY_DOMAIN}/coverImage/{image_id}"

    if 'f_auto' in image_id or 'q_auto' in image_id:
        return base_url
    
    return f"{settings.CLOUDINARY_DOMAIN}/f_auto,q_auto,c_scale,h_810/coverImage/{image_id}"

class RelatedArticleSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True)
    categories = CategorySerializer(many=True)
    thumb = serializers.SerializerMethodField()

    def get_thumb(self, obj):
        return get_cloudinary_url(obj.thumb)

    class Meta:
        model = Article
        fields = [
            "id",
            "slug",
            "title",
            "authors",
            "thumb",
            "categories",
            "summary",
            "min_read",
            "created_at",
        ]


class ArticleListSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)
    authors = AuthorSerializer(many=True)
    thumb = serializers.SerializerMethodField()

    def get_thumb(self, obj):
        return get_cloudinary_url(obj.thumb)

    class Meta:
        model = Article
        exclude = [
            "content",
            "scheduled_publish_time",
            "acknowledgement",
            "status",
            "views",
            "created_at",
            "updated_at",
            "table_of_contents",
            "gpt_summary",
            "related_articles",
        ]


class ArticleSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True)
    views = serializers.ReadOnlyField()
    min_read = serializers.ReadOnlyField()
    related_articles = serializers.SerializerMethodField()
    thumb = serializers.SerializerMethodField()

    def get_thumb(self, obj):
        return get_cloudinary_url(obj.thumb)

    def get_related_articles(self, obj):
        related = obj.get_related_articles()
        return RelatedArticleSerializer(related, many=True, context=self.context).data

    class Meta:
        model = Article
        fields = [
            "id",
            "slug",
            "title",
            "authors",
            "thumb",
            "categories",
            "summary",
            "acknowledgement",
            "content",
            "min_read",
            "status",
            "views",
            "gpt_summary",
            "created_at",
            "updated_at",
            "scheduled_publish_time",
            "table_of_contents",
            "is_sponsored",
            "sponsor_color",
            "sponsor_text_color",
            "related_articles",
        ]


class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating articles."""

    authors = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(), many=True, required=False
    )
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, required=False
    )
    related_articles = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.filter(status="ready"), many=True, required=False
    )

    class Meta:
        model = Article
        fields = [
            "title",
            "slug",
            "categories",
            "thumb",
            "content",
            "summary",
            "gpt_summary",
            "acknowledgement",
            "status",
            "authors",
            "scheduled_publish_time",
            "is_sponsored",
            "sponsor_color",
            "sponsor_text_color",
            "related_articles",
        ]

    def validate_related_articles(self, value):
        if len(value) > 3:
            raise serializers.ValidationError(
                "You can select up to 3 related articles only."
            )
        return value

    def create(self, validated_data: dict) -> Article:
        """Create a new article instance."""
        request = self.context.get("request")
        authors = validated_data.pop("authors", [])
        categories = validated_data.pop("categories", [])
        related_articles = validated_data.pop("related_articles", [])

        try:
            if not authors and request and hasattr(request, "user"):
                user_author = Author.objects.filter(user=request.user).first()
                if user_author:
                    authors = [user_author]

            article = Article(**validated_data)
            article.save()

            if authors:
                article.authors.set(authors)
            if categories:
                article.categories.set(categories)
            if related_articles is not None:
                article.related_articles.set(related_articles)

            return article
        except Exception as e:
            logging.error(f"Error creating article: {str(e)}")
            raise serializers.ValidationError("An error occurred while creating the article.") from e

    def update(self, instance: Article, validated_data: dict) -> Article:
        """Update an existing article instance."""
        authors = validated_data.pop("authors", [])
        categories = validated_data.pop("categories", [])
        related_articles = validated_data.pop("related_articles", [])

        try:
            instance = super().update(instance, validated_data)

            if authors:
                instance.authors.set(authors)
            if categories:
                instance.categories.set(categories)
            if related_articles is not None:
                instance.related_articles.set(related_articles)

            return instance
        except Exception as e:
            logging.error(f"Error updating article: {str(e)}")
            raise serializers.ValidationError("Error updating article.") from e