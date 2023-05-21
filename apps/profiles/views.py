from django.contrib.auth.models import Group
from rest_framework import status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings

from apps.profiles import serializers
from apps.profiles.models import UserNote, UserProfile, UserProfileManager
from apps.roles.models import (DEFAULT_MANAGER_ROLE_NAME,
                               DEFAULT_SALES_ROLE_NAME, Role)
from apps.utils.serializers import GetSerializerMixin

NOT_FOUND_RESPONSE = Response({"message": "Not Found"}, status=status.HTTP_404_NOT_FOUND)

class UserLoginApiView(ObtainAuthToken):
    """Handle creating user authentication tokens"""
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class UserProfileViewSet(viewsets.ModelViewSet, GetSerializerMixin):
    serializer_class = serializers.UserProfileSerializer
    serializer_action_classes = {
        "create": serializers.CreateUserProfileSerializer,
    }
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = UserProfile.objects.all()
    
    def create_user(self, email, first_name, last_name, password=None):
        """Create a new UserProfile"""
        user_manager: UserProfileManager = UserProfile.objects
        user = user_manager.create_user(
            tenant_id=self.request.user.tenant.id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        return user

    def get_queryset(self):
        return UserProfile.objects.filter(tenant=self.request.user.tenant)
    
    def list(self, request, *args, **kwargs):
        if not request.user.has_perm("profiles.list_userprofile"):
            return NOT_FOUND_RESPONSE
        
        queryset = self.filter_queryset(self.get_queryset())
        if not request.user.is_staff and request.user.role.name == f"{request.user.tenant.id}_{DEFAULT_MANAGER_ROLE_NAME}":
            queryset = queryset.filter(manager=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        user_to_get: UserProfile = self.get_object()
        if request.user.has_perm("profiles.view_userprofile"):
            return super().retrieve(request, *args, **kwargs)
        if user_to_get.id == request.user.id or request.user == user_to_get.manager:
            return super().retrieve(request, *args, **kwargs)
        return NOT_FOUND_RESPONSE
    
    def update(self, request, *args, **kwargs):
        if not request.user.is_staff and self.get_object().id != request.user.id:
            return NOT_FOUND_RESPONSE
        return super().update(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response({"message": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = serializers.CreateUserProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if self.get_queryset().filter(email=serializer.validated_data["email"]).exists():
            return Response({"error": "Email already in use"}, status=status.HTTP_400_BAD_REQUEST)
        user: UserProfile = self.create_user(
            email=serializer.validated_data["email"],
            first_name=serializer.validated_data["first_name"],
            last_name=serializer.validated_data["last_name"],
            password=serializer.validated_data["password"]
        )
        return Response({"message": f"Created user with email {user.email}"}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"])
    def update_password(self, request, pk=None):
        if not request.user.is_staff and self.get_object().id != request.user.id:
            return NOT_FOUND_RESPONSE
        serializer = serializers.ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user: UserProfile = self.get_object()
        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"message": "Updated password"}, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=True, methods=["patch"])
    def update_role(self, request, pk=None):
        if not request.user.has_perm("roles.change_role"):
            return NOT_FOUND_RESPONSE
        user_to_update: UserProfile = self.get_object()
        role_name = request.data["role"]
        role: Role = Role.objects.get(name=f"{request.user.tenant.id}_{role_name}")
        if user_to_update.role is not None:
            user_to_update.role.group.user_set.remove(user_to_update)
        user_to_update.role = role
        role.group.user_set.add(user_to_update)
        user_to_update.save()
        return Response({"message": "Updated role"}, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=True, methods=["patch"])
    def assign_manager(self, request, pk=None):
        if not request.user.has_perm("profiles.change_userprofile"):
            return NOT_FOUND_RESPONSE
        manager: UserProfile = UserProfile.objects.get(id=request.data["manager_id"])
        if manager.role.name != f"{request.user.tenant.id}_{DEFAULT_MANAGER_ROLE_NAME}":
            return Response({"message": "Only users with Manager role can be assigned as managers"}, status=status.HTTP_400_BAD_REQUEST)
        user: UserProfile = self.get_object()
        if user.role.name != f"{request.user.tenant.id}_{DEFAULT_SALES_ROLE_NAME}":
            return Response({"message": "Managers can only be assigned to sales users"}, status=status.HTTP_400_BAD_REQUEST)
        user.manager = manager
        user.save()
        return Response({"message": "Assigned to a manager"}, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=True, methods=["get"])
    def get_notes(self, request, pk=None):
        user: UserProfile = self.get_object()
        if not request.user.is_staff and request.user != user and request.user != user.manager:
            return NOT_FOUND_RESPONSE
        queryset = user.notes.all().order_by("-created_on")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.UserNoteSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.UserNoteSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def add_note(self, request, pk=None):
        user: UserProfile = self.get_object()
        if not request.user.is_staff and request.user != user and request.user != user.manager:
            return NOT_FOUND_RESPONSE
        note: UserNote = UserNote(tenant=user.tenant, user=user, note=request.data["note"])
        note.save()
        return Response({"message": "Note added"}, status=status.HTTP_201_CREATED)
