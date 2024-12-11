from rest_framework import serializers
from ..models import Article, Author, Category, RelatedArticle
from .author_serializer import AuthorSerializer
from .category_serializer import CategorySerializer

class ArticleListSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)
    authors = AuthorSerializer(many=True)

    class Meta:
        model = Article
        exclude = [
            'content', 'scheduled_publish_time', 'acknowledgement', 
            'status', 'views', 'created_at', 'updated_at', 'table_of_contents'
        ]
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
    """Serializer for the Article model."""
    authors = AuthorSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True)       
    views = serializers.ReadOnlyField()
    min_read = serializers.ReadOnlyField()
    related_articles = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = [
            'id', 'slug', 'title', 'authors', 'thumb', 'categories', 'summary',
            'acknowledgement', 'content', 'min_read', 'status', 'views',
            'created_at', 'updated_at', 'scheduled_publish_time', 'table_of_contents',
            'is_sponsored', 'sponsor_color', 'sponsor_text_color', 'related_articles'
        ]
        
    def get_related_articles(self, obj):
        """Return the related articles for the article."""
        related_articles = obj.get_related_articles()
        return ArticleListSerializer(related_articles, many=True).data

class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating articles."""
    authors = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all(), many=True, required=False)
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True, required=False)
    related_article_ids = serializers.PrimaryKeyRelatedField(queryset=Article.objects.filter(status='ready'), many=True, required=False, write_only=True)

    class Meta:
        model = Article
        fields = ['title', 'slug', 'categories', 'thumb', 'content', 'summary', 'acknowledgement', 'status', 'authors', 'scheduled_publish_time', 'is_sponsored', 'sponsor_color', 'sponsor_text_color', 'related_article_ids']
    
    def validate_related_articles_ids(self, value):
        """Validate related articles"""
        if len(value) > 3:
            raise serializers.ValidationError("You can only have a maximum of 3 related articles.")
        return value
    
    def create(self, validated_data: dict) -> Article:
        """Create a new article instance."""
        request = self.context.get('request')
        authors = validated_data.pop('authors', [])
        categories = validated_data.pop('categories', [])
        related_article_ids = validated_data.pop('related_article_ids', [])

        try:
            if not authors and request and hasattr(request, 'user'):
                user_author = Author.objects.filter(user=request.user).first()
                if user_author:
                    authors = [user_author]

            article = Article(**validated_data)
            article.save()

            if authors:
                article.authors.set(authors)
            if categories:
                article.categories.set(categories)
                
            # Handle related articles
            for related_article in related_article_ids:
                RelatedArticle.objects.create(
                    from_article=article, to_article=related_article
                )

            return article
        except Exception as e:            
            raise serializers.ValidationError(f"Error creating article: {str(e)}")


    def update(self, instance: Article, validated_data: dict) -> Article:
        """Update an existing article instance."""
        authors = validated_data.pop('authors', [])
        categories = validated_data.pop('categories', [])
        related_article_ids = validated_data.pop('related_article_ids', [])
        
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
        except Exception as e:          
            raise serializers.ValidationError(f"Error updating article: {str(e)}")
