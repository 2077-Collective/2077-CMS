from rest_framework import serializers
from ..models import Article, Author, Category
from .author_serializer import AuthorSerializer
from .category_serializer import CategorySerializer

class ArticleListSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)
    authors = AuthorSerializer(many=True)

    class Meta:
        model = Article
        include = ['categories' 'authors']
        exclude = [
            'content', 'scheduled_publish_time', 'acknowledgement', 
            'status', 'views', 'created_at', 'updated_at', 'table_of_contents'
        ]

class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for the Article model."""
    authors = AuthorSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True)       
    views = serializers.ReadOnlyField()
    min_read = serializers.ReadOnlyField()
    

    class Meta:
        model = Article
        fields = [
            'id', 'slug', 'title', 'authors', 'thumb', 'categories', 'summary',
            'acknowledgement', 'content', 'min_read', 'status', 'views',
            'created_at', 'updated_at', 'scheduled_publish_time', 'table_of_contents'
        ]

class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating articles."""
    authors = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all(), many=True, required=False)
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True, required=False)

    class Meta:
        model = Article
        fields = ['title', 'slug', 'categories', 'thumb', 'content', 'summary', 'acknowledgement', 'status', 'authors', 'scheduled_publish_time']
    
    def create(self, validated_data: dict) -> Article:
        """Create a new article instance."""
        request = self.context.get('request')
        authors = validated_data.pop('authors', [])
        categories = validated_data.pop('categories', [])

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

            return article
        except Exception as e:            
            raise serializers.ValidationError(f"Error creating article: {str(e)}")


    def update(self, instance: Article, validated_data: dict) -> Article:
        """Update an existing article instance."""
        authors = validated_data.pop('authors', [])
        categories = validated_data.pop('categories', [])
        try:
            instance = super().update(instance, validated_data)

            if authors:
                instance.authors.set(authors)
            if categories:
                instance.categories.set(categories)

            return instance
        except Exception as e:          
            raise serializers.ValidationError(f"Error updating article: {str(e)}")
