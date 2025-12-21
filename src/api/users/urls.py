from django.urls import path
from .views import UserListView, UserDetailView, UserRegisterView, UserLoginView

urlpatterns = [
    path('', UserListView.as_view(), name='users-list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('sign-up/', UserRegisterView.as_view(), name='user-register'),
    path("login/", UserLoginView.as_view()),
]
