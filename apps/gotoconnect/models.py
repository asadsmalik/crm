from django.db import models

from apps.tenants.models import TenantAwareModel


class GoToConnectConfig(TenantAwareModel):
    client_id = models.CharField("client_id", max_length=255, blank=True, null=True)
    client_secret = models.CharField(
        "client_secret", max_length=255, blank=True, null=True
    )


class GoToConnectUser(TenantAwareModel):
    user_profile = models.OneToOneField("profiles.UserProfile", on_delete=models.CASCADE)
    access_token = models.CharField("access_token", max_length=255)
    refresh_token = models.CharField("refresh_token", max_length=255)
    line_id = models.CharField("line_id", max_length=255, blank=True, null=True)
