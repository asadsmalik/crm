from django.db import models


class Tenant(models.Model):
    name = models.CharField(max_length=100)
    subdomain_prefix = models.CharField(max_length=100, unique=True)
    # Max number of prospects a user can lock at a single time
    max_prospects_per_user = models.IntegerField(default=10)
    # How long before user can re-lock an unlocked prospect
    prospect_cooldown_days = models.IntegerField(default=3)


class TenantAwareModel(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)

    class Meta:
        abstract = True

