from django.contrib.auth.mixins import PermissionRequiredMixin
from rest_framework import permissions

from apps.profiles.models import UserProfile


class IsAdminOrOwnProfile(permissions.BasePermission):
    """Allow admins all access OR users to update their own profile"""

    def has_object_permission(self, request, view, obj):
        user : UserProfile = request.user
        return user.is_staff or obj.id == user.id
