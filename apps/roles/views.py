
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.contacts.models import Contact, ContactNote
from apps.profiles.models import UserProfile
from apps.roles.models import (DEFAULT_ADMIN_ROLE_NAME,
                               DEFAULT_MANAGER_ROLE_NAME,
                               DEFAULT_SALES_ROLE_NAME, Role)
from apps.roles.serializers import CreateRoleSerializer, RoleSerializer
from apps.utils.serializers import GetSerializerMixin


class RoleViewSet(viewsets.ModelViewSet, GetSerializerMixin):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    serializer_action_classes = {
        "create": CreateRoleSerializer
    }

    def get_content_type(self, permission: str):
        permission_model = permission.split("_")[1]
        if "userprofile" == permission_model:
            return ContentType.objects.get_for_model(UserProfile)
        if "contact" == permission_model:
            return ContentType.objects.get_for_model(Contact)
        if "contactnote" == permission_model:
            return ContentType.objects.get_for_model(ContactNote)
        if "role" == permission_model:
            return ContentType.objects.get_for_model(Role)
        # TODO: Add for all models
        return None

    def extract_permissions(self, permissions_str: str):
        return [Permission.objects.get(codename=p, content_type=self.get_content_type(p)) for p in permissions_str.split(",")]

    def list(self, request, *args, **kwargs):
        user : UserProfile = request.user
        if not user.is_staff and not user.has_perm("roles.view_role"):
            return Response({"message": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        user : UserProfile = request.user
        if not user.is_staff and not user.has_perm("roles.add_role"):
            return Response({"message": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = CreateRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role_name = serializer.validated_data["name"]
        if self.get_queryset().filter(name=role_name, tenant=request.user.tenant).exists():
            return Response({"message": "Role already exists"}, status=status.HTTP_400_BAD_REQUEST)
        group: Group = Group.objects.create(name=f"{user.tenant.id}_{role_name}")
        permissions = self.extract_permissions(serializer.validated_data["permissions"])
        group.permissions.set(permissions)
        group.save()
        role: Role = Role(name=role_name, group=group, tenant=user.tenant)
        role.save()
        return Response({"message": f"Created new role {role_name}"}, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        user : UserProfile = request.user
        if not user.is_staff and not user.has_perm("roles.view_role"):
            return Response({"message": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        return super().retrieve(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        user : UserProfile = request.user
        if not user.is_staff and not user.has_perm("roles.change_role"):
            return Response({"message": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        role: Role = self.get_object()
        if role.name == DEFAULT_ADMIN_ROLE_NAME:
            return Response({"message": "Cannot update admin role"}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        user : UserProfile = request.user
        if not user.is_staff and not user.has_perm("roles.delete_role"):
            return Response({"message": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        role: Role = self.get_object()
        if role.name in [DEFAULT_ADMIN_ROLE_NAME, DEFAULT_MANAGER_ROLE_NAME, DEFAULT_SALES_ROLE_NAME]:
            return Response({"message": "Cannot delete default roles"}, status=status.HTTP_400_BAD_REQUEST)
        return super().destroy(request, *args, **kwargs)
