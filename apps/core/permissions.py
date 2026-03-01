"""
Custom permission classes for the Library Management System.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminUser(BasePermission):
    """
    Permission class that only allows Admin users.
    """
    message = "You must be an admin to perform this action."

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'ADMIN'
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Permission class that allows read-only access to anyone,
    but only admins can modify.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'ADMIN'
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Permission class that allows owners or admins to access/modify objects.
    """
    def has_object_permission(self, request, view, obj):
        # Admin has full access
        if request.user.role == 'ADMIN':
            return True

        # Check if the object has a user field
        if hasattr(obj, 'user'):
            return obj.user == request.user

        # If the object is the user itself
        return obj == request.user


class IsMemberUser(BasePermission):
    """
    Permission class that only allows Member users.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'MEMBER'
        )
