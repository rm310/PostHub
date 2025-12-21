from rest_framework import generics
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from src.api.users.serializers import UserRegisterSerializer
from src.api.users.serializers.usersserializer import UsersSerializer
from src.apps.users.models import Users

class UserRegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

class UserListView(ListAPIView):
    queryset = Users.objects.filter(is_active=True)
    serializer_class = UsersSerializer
    permission_classes = [IsAuthenticated]

class UserDetailView(RetrieveAPIView):
    queryset = Users.objects.filter(is_active=True)
    serializer_class = UsersSerializer
    permission_classes = [IsAuthenticated]

from rest_framework_simplejwt.views import TokenObtainPairView

class UserLoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

