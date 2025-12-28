import uuid
from django.core.cache import cache
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from src.api.users.serializers import UserRegisterSerializer, UsersSerializer, TokenConfirmSerializer
from src.apps.users.models import Users

from .utils import standard_response
from rest_framework import status
import uuid


class UserRegisterInitView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)

        # Manual check to return our custom structured response on validation error
        if not serializer.is_valid():
            return standard_response(
                success=False,
                message="Validation failed.",
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        reg_token = str(uuid.uuid4())
        user_data = serializer.validated_data

        # Store in Redis
        cache.set(f"pending_user_{reg_token}", user_data, timeout=600)

        return standard_response(
            success=True,
            message="Verification token generated successfully.",
            data={"token": reg_token},
            status_code=status.HTTP_200_OK
        )


class UserRegisterConfirmView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = TokenConfirmSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return standard_response(
                success=False,
                message="Invalid request data.",
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        token = serializer.validated_data.get('token')
        user_data = cache.get(f"pending_user_{token}")

        if not user_data:
            return standard_response(
                success=False,
                message="Invalid or expired token.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Create the user
            user = Users.objects.create_user(**user_data)
            cache.delete(f"pending_user_{token}")

            # Generate JWT
            refresh = RefreshToken.for_user(user)

            payload = {
                "user_id": user.id,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }
            }

            return standard_response(
                success=True,
                message="User account created and confirmed successfully.",
                data=payload,
                status_code=status.HTTP_201_CREATED
            )

        except Exception as e:
            return standard_response(
                success=False,
                message=f"An error occurred during creation: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


from .utils import standard_response
from rest_framework import status


class UserListView(generics.ListAPIView):
    queryset = Users.objects.filter(is_active=True)
    serializer_class = UsersSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Handling pagination if you have it enabled
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        # Your professional structure
        return standard_response(
            success=True,
            message="Users list retrieved successfully.",
            data={"users": serializer.data},
            status_code=status.HTTP_200_OK
        )


class UserDetailView(generics.RetrieveAPIView):
    queryset = Users.objects.filter(is_active=True)
    serializer_class = UsersSerializer
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # Your professional structure
        return standard_response(
            success=True,
            message="User details retrieved successfully.",
            data={"user": serializer.data},
            status_code=status.HTTP_200_OK
        )


class UserLoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            # SimpleJWT raises AuthenticationFailed here if credentials are wrong
            serializer.is_valid(raise_exception=True)

            return standard_response(
                success=True,
                message="Login successful.",
                data=serializer.validated_data,
                status_code=status.HTTP_200_OK
            )

        except AuthenticationFailed as e:
            # This catches the "No active account found" error
            return standard_response(
                success=False,
                message="Invalid username or password.",
                data={"detail": str(e)},
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            # This catches other validation errors (like missing fields)
            return standard_response(
                success=False,
                message="Login failed.",
                data=serializer.errors if hasattr(serializer, '_errors') else {"detail": str(e)},
                status_code=status.HTTP_400_BAD_REQUEST
            )

class UserUpdateInitView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserRegisterSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data, partial=True)

        if not serializer.is_valid():
            return standard_response(
                success=False,
                message="Validation failed for update data.",
                data=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        user_id = str(request.user.id)
        cache_key = f"pending_update_{user_id}"

        # Store the validated data in Redis
        cache.set(cache_key, serializer.validated_data, timeout=600)

        return standard_response(
            success=True,
            message="Update request stored in Redis. Please confirm to apply changes.",
            data={"cache_key": cache_key}
        )


class UserUpdateConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = str(request.user.id)
        cache_key = f"pending_update_{user_id}"
        pending_data = cache.get(cache_key)

        if not pending_data:
            return standard_response(
                success=False,
                message="No pending updates found or session expired.",
                data={"attempted_key": cache_key},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Apply data from Redis to the authenticated user
        user = request.user
        for attr, value in pending_data.items():
            if attr == 'password':
                user.set_password(value)
            else:
                setattr(user, attr, value)

        user.save()
        cache.delete(cache_key)

        return standard_response(
            success=True,
            message="Profile updated successfully.",
            data={"user_id": user.id}
        )


class UserDeleteInitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Mark this specific user as "pending deletion" in Redis
        user_id = str(request.user.id)
        cache_key = f"delete_request_{user_id}"

        cache.set(cache_key, True, timeout=300)

        return standard_response(
            success=True,
            message="Deletion initialized. Please call confirm within 5 minutes to permanently remove your account.",
            data={"expires_in": "300 seconds"}
        )


class UserDeleteConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_id = str(request.user.id)
        cache_key = f"delete_request_{user_id}"

        if not cache.get(cache_key):
            return standard_response(
                success=False,
                message="Delete request not found or expired.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # Final action: Delete the user from the database
        request.user.delete()

        # Clean up Redis
        cache.delete(cache_key)

        return standard_response(
            success=True,
            message="Account deleted successfully.",
            data={},
            status_code=status.HTTP_200_OK
        )