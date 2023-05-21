from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from apps.tenants.models import TenantAwareModel


class Lifecycle(models.TextChoices):
    LEAD = "LEAD", _("Lead")
    PROSPECT = "PROSPECT", _("Prospect")
    CUSTOMER = "CUSTOMER", _("Customer")


class TimeZone(models.TextChoices):
    EST = "EST"
    CST = "CST"
    PST = "PST"


class Contact(TenantAwareModel):

    # Contact Info
    name = models.CharField("name", max_length=255)
    address_1 = models.CharField("address_1", max_length=255)
    address_2 = models.CharField("address_2", max_length=255, null=True, blank=True)
    city = models.CharField("city", max_length=100)
    state = models.CharField("state", max_length=2)
    zip_code = models.CharField("zip_code", max_length=10)
    email = models.EmailField("email", max_length=255, null=True)
    logo = models.CharField(max_length=255, null=True, blank=True)  # TODO: Replace with slug maybe?
    timezone = models.CharField(
        "timezone", choices=TimeZone.choices, max_length=3, default=TimeZone.EST
    )

    # Create Info
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="contacts_added",  # This is how a user can refer to all contacts he/she created
    )
    created_on = models.DateTimeField("created_on", auto_now_add=True)
    lifecycle_updated_on = models.DateTimeField("lifecycle_updated_on", null=True)

    # Quality Info
    lifecycle_status = models.CharField(
        "lifecycle_status",
        choices=Lifecycle.choices,
        max_length=40,
        default=Lifecycle.LEAD,
    )
    rating = models.IntegerField(
        default=1, validators=(MinValueValidator(1), MaxValueValidator(5))
    )

    # Lifecycle Info
    is_locked = models.BooleanField(default=False)
    locked_on = models.DateTimeField("locked_on", null=True)
    customer_of = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="my_customers",
    )
    locked_by = models.ForeignKey(
        "profiles.UserProfile",
        on_delete=models.SET_NULL,
        null=True,
        related_name="locked_contacts",
    )

    class Meta:
        unique_together = ("tenant", "name")

    def __str__(self) -> str:
        return f"{self.name}"


# TODO: Ensure that each Contact has at least 1 ContactAssociate
# TODO: Create the initial contact when contact created
# TODO: Do not allow deletion if only 1 ContactAssociate exists
class ContactAssociate(TenantAwareModel):
    name = models.CharField("name", max_length=255)
    phone_number = PhoneNumberField(null=True, unique=True)
    phone_number_ext = models.IntegerField(null=True)
    designation = models.CharField("designation", max_length=100)
    email = models.EmailField("email", max_length=255, null=True, unique=True)
    contact = models.ForeignKey(
        "Contact", on_delete=models.CASCADE, related_name="contact_associates"
    )
    created_by = models.ForeignKey(
        "profiles.UserProfile", on_delete=models.SET_NULL, null=True
    )

    class Meta:
        unique_together = ("tenant", "phone_number", "email")

    def __str__(self) -> str:
        return f"{self.name} <{self.email}> <{self.phone_number}>"


class ContactNote(TenantAwareModel):
    contact = models.ForeignKey(
        "Contact", on_delete=models.CASCADE, related_name="notes"
    )
    created_on = models.DateTimeField(auto_now_add=True)
    body = models.TextField(null=False, blank=False)

    def __str__(self) -> str:
        return f"<{self.contact.name} <{self.created_on}> <{self.body}>"


class ContactTimeline(TenantAwareModel):
    contact = models.ForeignKey(
        "Contact", on_delete=models.CASCADE, related_name="timeline"
    )
    created_on = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, null=False, blank=False)

    def __str__(self) -> str:
        return f"<{self.contact.name} <{self.created_on}> <{self.title}>"
