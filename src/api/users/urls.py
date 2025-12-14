from django.urls import path
from .views import UserListView, UserDetailView, UserRegisterView

urlpatterns = [
    path('', UserListView.as_view(), name='users-list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('register/', UserRegisterView.as_view(), name='user-register'),
]
