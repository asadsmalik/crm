from rest_framework import serializers

from .models import GoToConnectConfig


class GoToConnectConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoToConnectConfig
        fields = "__all__"
