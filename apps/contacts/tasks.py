from celery import shared_task
from celery.schedules import crontab
from logistics_crm.celery import app

from apps.tenants.models import Tenant


@app.on_after_finalize.connect
def setup_prospect_unlock(sender, **kwargs):
    # sender.add_periodic_task(10.0, unlock_prospects.s(), name='add every 10')
    # Executes every day at 12:30 a.m. PST
    sender.add_periodic_task(
        crontab(hour=0, minute=30, day_of_week=1),
        unlock_prospects.s(),
    )

@app.task
def unlock_prospects():
    # TODO: Implement this
    tenants = Tenant.objects.all()
    for tenant in tenants:
        print(f"Unlocking contacts for tenant: {tenant.name}")
