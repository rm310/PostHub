from django.db.models import Count, Q
from rest_framework import generics
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from src.api.posts.serializers import PostSerializer, LikeSerializer, CommentSerializer, PostCreateSerializer
from src.apps.posts.models import Post, Like, Comment

class PostBaseQuerysetMixin:
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Post.objects.none()
        user = self.request.user
        return Post.objects.filter(
            Q(status='published') | Q(user=user)
        ).select_related('user').annotate(
            likes_count=Count('likes', distinct=True),
            comments_count=Count('comments', distinct=True),
        ).order_by('-created_at')


class PostListView(PostBaseQuerysetMixin, generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny]


class PostCreateView(generics.CreateAPIView):
    serializer_class = PostCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



class PostDetailView(PostBaseQuerysetMixin, generics.RetrieveAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

class MyPostListView(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Post.objects
            .filter(user=self.request.user)
            .select_related('user')
            .annotate(
                likes_count=Count('likes', distinct=True),
                comments_count=Count('comments', distinct=True),
            )
            .order_by('-created_at')
        )

class LikeListView(generics.ListAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Like.objects.filter(post_id=post_id)

class LikeCreateView(generics.CreateAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = Post.objects.get(pk=post_id)
        serializer.save(user=self.request.user, post=post)

class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(post_id=post_id)

class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = Post.objects.get(pk=post_id)
        serializer.save(user=self.request.user, post=post)



