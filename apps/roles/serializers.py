from rest_framework import serializers

from apps.roles.constants import MAX_ROLE_NAME_LENGTH
from apps.roles.models import Role


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"
        read_only_fields = ["name"]


class CreateRoleSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=MAX_ROLE_NAME_LENGTH)
    permissions = serializers.CharField()
    
