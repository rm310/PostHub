from src.api.users.views import UserRegisterInitView, UserRegisterConfirmView, UserLoginView, UserListView, \
    UserDetailView, UserUpdateInitView, UserUpdateConfirmView, UserDeleteInitView, UserDeleteConfirmView

from django.urls import path

urlpatterns = [
    path('auth/register/init/', UserRegisterInitView.as_view(), name='reg-init'),
    path('auth/register/confirm/', UserRegisterConfirmView.as_view(), name='reg-confirm'),

    path('auth/login/', UserLoginView.as_view(), name='login'),

    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),

    path('update/init/', UserUpdateInitView.as_view(), name='user-update-init'),
    path('update/confirm/', UserUpdateConfirmView.as_view(), name='user-update-confirm'),

    path('delete/init/', UserDeleteInitView.as_view(), name='user-delete-init'),
    path('delete/confirm/', UserDeleteConfirmView.as_view(), name='user-delete-confirm'),
]
