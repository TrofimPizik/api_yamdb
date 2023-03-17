from rest_framework import permissions


class AdminOnly(permissions.BasePermission):
    """
    Разрешение на редактирование только для администратора.
    """
    def has_permission(self, request, view):
        return request.user.is_admin or request.user.is_staff