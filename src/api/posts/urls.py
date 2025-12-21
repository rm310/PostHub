from django.urls import path
from .views import (
    PostDetailView, PostCreateView,
    MyDraftPostListView, MyPublishedPostListView,
    LikeListView, LikeCreateView,
    CommentListView, CommentCreateView, PublicPostListView
)

urlpatterns = [
    path('', PublicPostListView.as_view(), name='post-list'),

    path('my/drafts/', MyDraftPostListView.as_view(), name='post-my-drafts'),  # only drafts
    path('my/published/', MyPublishedPostListView.as_view(), name='post-my-published'), # only published

    path('create/', PostCreateView.as_view(), name='post-create'),

    path('<int:pk>/', PostDetailView.as_view(), name='post-detail'),

    path('<int:post_id>/likes/', LikeListView.as_view(), name='post-like-list'),
    path('<int:post_id>/likes/create/', LikeCreateView.as_view(), name='post-like-create'),

    path('<int:post_id>/comments/', CommentListView.as_view(), name='post-comment-list'),
    path('<int:post_id>/comments/create/', CommentCreateView.as_view(), name='post-comment-create'),
]
