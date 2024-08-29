from rest_framework import serializers
from ..models import Author

class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for the Author model."""
    username = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ['id', 'username', 'full_name', 'bio', 'twitter_username']

    def get_username(self, obj):
        return obj.user.username
