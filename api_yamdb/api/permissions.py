from rest_framework import permissions

from users.models import User


class AuthorAccess(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )


class ModeratorAccess(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.role == User.MODERATOR
        )


class AdminAccess(permissions.BasePermission):
    def has_permission(self, request, view,):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.role == User.ADMIN
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.role == User.ADMIN
        )


class AdminOnly(permissions.BasePermission):
    """
    Разрешение на редактирование только для администратора.
    """
    def has_permission(self, request, view):
        return request.user.is_admin or request.user.is_staff
