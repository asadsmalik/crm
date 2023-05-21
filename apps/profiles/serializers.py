from dataclasses import fields

from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from .models import UserNote, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        read_only_fields = ["tenant", "role"]
        exclude = ["password"]


class CreateUserProfileSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    class Meta:
        model = UserProfile
        fields = ["email", "first_name", "last_name", "password", "confirm_password"]
        extra_kwargs = {
            "password": {"write_only": True, "style": {"input_type": "password"}}
        }

        def validate_password(self, value):
            validate_password(value)
            return value

        def validate(self, data):
            if data["password"] != data["confirm_password"]:
                raise serializers.ValidationError(
                    _("Confirm password does not match password")
                )
            return data
        


class ChangePasswordSerializer(serializers.Serializer):
    model = UserProfile
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        if user is None:
            raise serializers.ValidationError(
                _("Could not fetch user profile")
            )
        if not user.check_password(value):
            raise serializers.ValidationError(
                _("Your old password was incorrect. Please enter it again")
            )
        return value

    def validate_new_password(self, value):
        validate_password(value)
        return value
    
    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError(
                _("Your new password did not match")
            )
        return data


class ResetPasswordSerializer(serializers.Serializer):
    pass

class UserNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNote
        fields = "__all__"
        read_only_fields = ["user", "created_on", "note"]
