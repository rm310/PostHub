from rest_framework import serializers

from src.apps.posts.models import Post
from src.apps.users.models import Users

class PostAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'username', 'profile_image']

class PostSerializer(serializers.ModelSerializer):
    user = PostAuthorSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'body', 'photo', 'user', 'status', 'created_at', 'updated_at', 'likes_count', 'comments_count']

class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'body', 'photo', 'status']
