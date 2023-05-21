from rest_framework import permissions


class ViewContactPermissions(permissions.BasePermission):
    """Allow Users to only view their own or unlocked contacts"""

    def has_object_permission(self, request, view, obj):
        user_tenant = request.user.tenant
        contact_tenant = obj.tenant
        if user_tenant.id != contact_tenant.id:
            return False
        if obj.locked_by is not None:
            return obj.locked_by.id == request.user.id
        return True
