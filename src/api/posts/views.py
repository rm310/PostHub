from django.db.models import Count, Q
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny

from src.api.posts.serializers import PostSerializer, LikeSerializer, CommentSerializer, PostCreateSerializer
from src.api.users.utils import standard_response
from src.apps.posts.models import Post, Like, Comment
from rest_framework import generics, status
from django.db.models import Count, Q

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



class PublicPostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Post.objects.filter(status='published').order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return standard_response(
            success=True,
            message="Public posts retrieved successfully.",
            data={"posts": serializer.data}
        )


class PostCreateView(generics.CreateAPIView):
    serializer_class = PostCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return standard_response(
                success=False,
                message="Post creation failed.",
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Save logic
        post_instance = serializer.save(user=self.request.user)
        return standard_response(
            success=True,
            message="Post created successfully.",
            data=PostSerializer(post_instance).data,  # Return the full post info
            status_code=status.HTTP_201_CREATED
        )


class PostDetailView(PostBaseQuerysetMixin, generics.RetrieveAPIView):
    serializer_class = PostSerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return standard_response(
            success=True,
            message="Post details retrieved.",
            data={"post": serializer.data}
        )


class PostUpdateView(generics.UpdateAPIView):
    serializer_class = PostCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Post.objects.none()
        return Post.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if not serializer.is_valid():
            return standard_response(
                success=False,
                message="Update failed.",
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        updated_instance = serializer.save()
        return standard_response(
            success=True,
            message="Post updated successfully.",
            data=PostSerializer(updated_instance).data
        )


class PostDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Post.objects.none()
        return Post.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return standard_response(
            success=True,
            message="Post deleted successfully.",
            data={}
        )


class MyPublishedPostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user, status='published')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return standard_response(
            success=True,
            message="Your published posts.",
            data={"posts": serializer.data}
        )


class MyDraftPostListView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user, status='draft')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return standard_response(
            success=True,
            message="Your draft posts.",
            data={"posts": serializer.data}
        )


class LikeListView(generics.ListAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)

        user = self.request.user
        if post.status == 'draft' and post.user != user:
            # We will handle this in the list method for consistency
            return None

        return Like.objects.filter(post_id=post_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset is None:
            return standard_response(
                success=False,
                message="Cannot view likes for someone else's draft.",
                status_code=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(queryset, many=True)
        return standard_response(
            success=True,
            message="Likes retrieved successfully.",
            data={"likes": serializer.data}
        )


class LikeCreateView(generics.CreateAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        post_id = self.kwargs.get('post_id')
        user = self.request.user
        post = get_object_or_404(Post, pk=post_id)

        if post.status == 'draft' and post.user != user:
            return standard_response(
                success=False,
                message="Cannot like someone else's draft.",
                status_code=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return standard_response(
                success=False,
                message="Validation error.",
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        like_instance = serializer.save(user=user, post=post)
        return standard_response(
            success=True,
            message="Post liked successfully.",
            data=LikeSerializer(like_instance).data,
            status_code=status.HTTP_201_CREATED
        )


class CommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)

        user = self.request.user
        if post.status == 'draft' and post.user != user:
            return None

        return Comment.objects.filter(post_id=post_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset is None:
            return standard_response(
                success=False,
                message="Cannot view comments for someone else's draft.",
                status_code=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(queryset, many=True)
        return standard_response(
            success=True,
            message="Comments retrieved successfully.",
            data={"comments": serializer.data}
        )


class CommentCreateView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        post_id = self.kwargs.get('post_id')
        user = self.request.user
        post = get_object_or_404(Post, pk=post_id)

        if post.status == 'draft' and post.user != user:
            return standard_response(
                success=False,
                message="Cannot comment on someone else's draft.",
                status_code=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return standard_response(
                success=False,
                message="Validation error.",
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        comment_instance = serializer.save(user=user, post=post)
        return standard_response(
            success=True,
            message="Comment added successfully.",
            data=CommentSerializer(comment_instance).data,
            status_code=status.HTTP_201_CREATED
        )



