from rest_framework import serializers
from ..models import Article, Author, Category
from .author_serializer import AuthorSerializer
from .category_serializer import CategorySerializer

class ArticleSerializer(serializers.ModelSerializer):
    """Serializer for the Article model."""
    authors = AuthorSerializer(many=True, read_only=True)
    categories = CategorySerializer(many=True)
    slug = serializers.ReadOnlyField()    
    views = serializers.ReadOnlyField()

    class Meta:
        model = Article
        fields = [
            'id', 'slug', 'title', 'authors', 'thumb', 
            'categories', 'summary', 'content', 
            'status', 'views', 'created_at', 'updated_at', 'scheduled_publish_time'
        ]

class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating articles."""
    authors = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all(), many=True, required=False)
    categories = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), many=True, required=False)

    class Meta:
        model = Article
        fields = ['title', 'categories', 'thumb', 'content', 'summary', 'status', 'authors', 'scheduled_publish_time']

    # TODO : Debug this method to add the logged-in user as the author when creating a new article
    def create(self, validated_data):
        request = self.context.get('request')
        authors = validated_data.pop('authors', [])
        categories = validated_data.pop('categories', [])

        if not authors and request and hasattr(request, 'user'):
            user_author = Author.objects.filter(user=request.user).first()
            if user_author:
                authors = [user_author]

        article = Article.objects.create(**validated_data)

        if authors:
            article.authors.set(authors)
        if categories:
            article.categories.set(categories)

        return article


    def update(self, instance, validated_data):
        authors = validated_data.pop('authors', [])
        categories = validated_data.pop('categories', [])
        
        instance = super().update(instance, validated_data)
        
        if authors:
            instance.authors.set(authors)
        if categories:
            instance.categories.set(categories)
            
        return instance
