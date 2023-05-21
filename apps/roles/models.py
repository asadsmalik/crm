from django.contrib.auth.models import Group
from django.db import models

from apps.roles.constants import MAX_ROLE_NAME_LENGTH
from apps.tenants.models import TenantAwareModel

DEFAULT_ADMIN_ROLE_NAME = "Admin"
DEFAULT_MANAGER_ROLE_NAME = "Manager"
DEFAULT_SALES_ROLE_NAME = "Sales"

class Role(TenantAwareModel):
    name = models.CharField(max_length=MAX_ROLE_NAME_LENGTH)
    group = models.OneToOneField(Group, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name
