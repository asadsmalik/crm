from datetime import datetime, timedelta

from django.utils.translation import gettext as _
from rest_framework.exceptions import APIException
from rest_framework.response import Response

from apps.profiles.models import UserProfile
from apps.utils.db_helper import save_models_in_transaction

from .models import Contact, ContactTimeline, Lifecycle


class ContactAlreadyLocked(APIException):
    def __init__(self, detail="Contact is already locked!") -> None:
        self._detail = detail
        super().__init__(detail=self._detail)


class ContactAlreadyUnlocked(APIException):
    def __init__(self, detail="Contact is already unlocked!") -> None:
        self._detail = detail
        super().__init__(detail=self._detail)


class CustomerNotLockable(APIException):
    def __init__(self, detail="Customers cannot be locked!") -> None:
        self._detail = detail
        super().__init__(detail=self._detail)


class ContactCooldown(APIException):
    def __init__(self, detail: str) -> None:
        self._detail = detail
        super().__init__(detail=self._detail)


class ContactLifecycleController:
    def __init__(self, contact: Contact) -> None:
        self._contact: Contact = contact

    def lock_contact(self, user: UserProfile):
        if self._contact.is_locked:
            raise ContactAlreadyLocked()
        if self._contact.lifecycle_status == Lifecycle.CUSTOMER:
            raise CustomerNotLockable()

        cooldown_time_remaining = self.get_cooldown_remaining(user=user)
        if cooldown_time_remaining > timedelta(0):
            raise ContactCooldown(
                detail=f"Cannot lock prospect for {cooldown_time_remaining}"
            )
        if user.total_contacts_locked == user.tenant.max_prospects_per_user:
            return Response(
                {"message": "Max number of prospects locked. Cannot lock more!"}
            )
        self._contact.is_locked = True
        self._contact.locked_on = datetime.now()
        self._contact.locked_by = user
        self._contact.customer_of = None
        user.total_contacts_locked += 1
        event = self.create_timeline_event(
            user=user, title=f"Contact Locked By: {user.__str__()}"
        )
        save_models_in_transaction(model_list=[self._contact, user, event])
        return Response({"message": "Successfully locked contact"})

    def get_cooldown_remaining(self, user: UserProfile):
        cooldown_days: int = user.tenant.prospect_cooldown_days
        if self._contact.locked_by is None:
            return timedelta(0)
        if self._contact.locked_by.id != user.id:
            return timedelta(0)
        unlocked_since = (
            datetime.now().timestamp() - self._contact.locked_on.timestamp()
        )
        return timedelta(days=cooldown_days) - timedelta(milliseconds=unlocked_since)

    def update_lifecycle_status(self, user: UserProfile, status: Lifecycle):
        if self._contact.lifecycle_status == status:
            return

        if status == Lifecycle.CUSTOMER:
            if self._contact.is_locked:
                user.total_contacts_locked -= 1
            self._contact.customer_of = user
            self._contact.is_locked = True
            self._contact.locked_by = None
            user.total_customers += 1
        if status == Lifecycle.PROSPECT:
            if self._contact.lifecycle_status == Lifecycle.CUSTOMER:
                user.total_customers -= 1
                self._contact.customer_of = None

        event = self.create_timeline_event(
            user, f"Contact updated from {self._contact.lifecycle_status} to {status}"
        )
        self._contact.lifecycle_updated_on = datetime.now()
        self._contact.lifecycle_status = status
        save_models_in_transaction(model_list=[self._contact, user, event])


    def unlock_contact(self, user: UserProfile):
        if not self._contact.is_locked:
            raise ContactAlreadyUnlocked()
        if self._contact.lifecycle_status == Lifecycle.CUSTOMER:
            raise CustomerNotLockable()

        self._contact.is_locked = False
        user.total_contacts_locked -= 1
        event = self.create_timeline_event(
            user=user, title=f"Contact unlocked by: {user.get_full_name()}"
        )
        save_models_in_transaction(model_list=[self._contact, user, event])
        return Response({"message": "Successfully unlocked contact"})

    def create_timeline_event(self, user: UserProfile, title: str):
        event = ContactTimeline()
        event.tenant = self._contact.tenant
        event.contact = self._contact
        event.title = title
        return event
