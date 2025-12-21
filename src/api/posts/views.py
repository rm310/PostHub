from django.db.models import Count, Q
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny

from src.api.posts.serializers import PostSerializer, LikeSerializer, CommentSerializer, PostCreateSerializer
from src.apps.posts.models import Post, Like, Comment

class PostBaseQuerysetMixin:
    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Post.objects.none()

        qs = (
            Post.objects
            .select_related('user')
            .annotate(
                likes_count=Count('likes', distinct=True),
                comments_count=Count('comments', distinct=True),
            )
            .order_by('-created_at')
        )

        user = self.request.user

        if user.is_authenticated:
            return qs.filter(
                Q(status='published') | Q(user=user)
            )

        return qs.filter(status='published')


class PublicPostListView(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Post.objects.filter(status='published')



class PostCreateView(generics.CreateAPIView):
    serializer_class = PostCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PostDetailView(PostBaseQuerysetMixin, generics.RetrieveAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

class MyPublishedPostListView(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(
            user=self.request.user,
            status='published'
        )

class MyDraftPostListView(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(
            user=self.request.user,
            status='draft'
        )


class LikeListView(generics.ListAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)

        user = self.request.user
        if post.status == 'draft' and post.user != user:
            raise PermissionDenied("Cannot view likes for someone else's draft.")

        return Like.objects.filter(post_id=post_id)

class LikeCreateView(generics.CreateAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        user = self.request.user
        post = get_object_or_404(Post, pk=post_id)

        if post.status == 'draft' and post.user != user:
            raise PermissionDenied("Cannot like someone else's draft.")

        serializer.save(user=user, post=post)

class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)

        user = self.request.user
        if post.status == 'draft' and post.user != user:
            raise PermissionDenied("Cannot view comments for someone else's draft.")

        return Comment.objects.filter(post_id=post_id)

class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        user = self.request.user
        post = get_object_or_404(Post, pk=post_id)

        if post.status == 'draft' and post.user != user:
            raise PermissionDenied("Cannot comment on someone else's draft.")

        serializer.save(user=user, post=post)



