"""
Views for the Users app.
"""

from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from apps.core.permissions import IsAdminUser
from apps.core.pagination import StandardResultsSetPagination
from .serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserProfileSerializer,
    AdminUserCreateSerializer,
    ChangePasswordSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    Public registration endpoint for new Members.
    No authentication required.

    POST /api/v1/users/register/
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                'message': 'User registered successfully.',
                'user': UserProfileSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Endpoint for users to view and update their own profile.

    GET /api/v1/users/profile/
    PUT/PATCH /api/v1/users/profile/
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    """
    Endpoint for users to change their password.

    POST /api/v1/users/change-password/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response(
            {'message': 'Password changed successfully.'},
            status=status.HTTP_200_OK
        )


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Admin to manage users.
    Admin only access.

    GET /api/v1/users/ - List all users
    POST /api/v1/users/ - Create a new user
    GET /api/v1/users/{id}/ - Retrieve a user
    PUT /api/v1/users/{id}/ - Update a user
    PATCH /api/v1/users/{id}/ - Partial update
    DELETE /api/v1/users/{id}/ - Deactivate a user
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return AdminUserCreateSerializer
        return UserSerializer

    def destroy(self, request, *args, **kwargs):
        """Soft delete - deactivate user instead of deleting."""
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response(
            {'message': 'User deactivated successfully.'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Reactivate a deactivated user."""
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response(
            {'message': 'User activated successfully.'},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def admins(self, request):
        """List all admin users."""
        admins = self.queryset.filter(role='ADMIN')
        page = self.paginate_queryset(admins)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(admins, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def members(self, request):
        """List all member users."""
        members = self.queryset.filter(role='MEMBER')
        page = self.paginate_queryset(members)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(members, many=True)
        return Response(serializer.data)
