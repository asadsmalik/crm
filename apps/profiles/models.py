from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models

from apps.tenants.models import Tenant, TenantAwareModel


class UserProfileManager(BaseUserManager):
    """Manager for UserProfile"""

    def create_user(self, tenant_id, email, first_name, last_name, password=None):
        """Create a new UserProfile"""
        if not email:
            raise TypeError("User must have an email address")
        normalized_email = self.normalize_email(email)
        tenant = Tenant.objects.filter(id=tenant_id).first()
        user: UserProfile = UserProfile(
            tenant=tenant,
            email=normalized_email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, tenant, email, first_name, last_name, password):
        user = self.create_user(tenant_id=tenant, email=email, first_name=first_name, last_name=last_name, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class UserProfile(AbstractBaseUser, TenantAwareModel, PermissionsMixin):

    email = models.EmailField("email", max_length=255, unique=True, db_index=True)
    first_name = models.CharField("first_name", max_length=255)
    last_name = models.CharField("last_name", max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_contacts_locked = models.IntegerField("total_contacts_locked", default=0)
    total_customers = models.IntegerField("total_customers", default=0)
    role = models.ForeignKey("roles.Role", on_delete=models.DO_NOTHING, null=True)
    manager = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, related_name="manager_of")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["tenant", "first_name", "last_name"]

    objects = UserProfileManager()

    class Meta:
        permissions = (("list_userprofile", "Can list user profiles"),)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} <{self.email}>"


class UserNote(TenantAwareModel):
    user = models.ForeignKey("profiles.UserProfile", on_delete=models.CASCADE, related_name="notes")
    created_on = models.DateTimeField(auto_now_add=True)
    note = models.TextField(null=False, blank=False)
