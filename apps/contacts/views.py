from datetime import datetime, timedelta

from rest_framework import filters, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from apps.profiles.models import UserProfile
from apps.utils.db_helper import save_models_in_transaction
from apps.utils.serializers import GetSerializerMixin
from apps.utils.tenants import get_tenant_from_request

from .controllers import ContactLifecycleController
from .models import Contact, ContactNote, Lifecycle
from .permissions import ViewContactPermissions
from .serializers import (ContactListSerializer, ContactNoteSerializer,
                          ContactSerializer, ContactTimelineSerializer)


class ContactViewSet(GetSerializerMixin, viewsets.ModelViewSet):
    serializer_class = ContactSerializer
    serializer_action_classes = {
        "list": ContactListSerializer,
    }
    queryset = Contact.objects.all()
    authentication_classes = (TokenAuthentication,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name", "email", "state", "city")
    permission_classes = (ViewContactPermissions,)

    def get_queryset(self):
        tenant = get_tenant_from_request(self.request)
        return super().get_queryset().filter(tenant=tenant)

    def perform_create(self, serializer):
        tenant = get_tenant_from_request(self.request)
        return serializer.save(tenant=tenant)

    @action(detail=True, methods=["patch"])
    def lock(self, request, pk=None):
        user: UserProfile = request.user
        contact: Contact = self.get_object()
        controller = ContactLifecycleController(contact=contact)
        return controller.lock_contact(user=user)

    @action(detail=True, methods=["patch"])
    def unlock(self, request, pk=None):
        user: UserProfile = request.user
        contact: Contact = self.get_object()
        controller = ContactLifecycleController(contact=contact)
        return controller.unlock_contact(user=user)

    @action(detail=True, methods=["patch"])
    def convert_to_customer(self, request, pk=None):
        user: UserProfile = request.user
        contact: Contact = self.get_object()
        controller = ContactLifecycleController(contact=contact)
        controller.update_lifecycle_status(user=user, status=Lifecycle.CUSTOMER)
        return Response({"message": "Converted to customer"}, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=["patch"])
    # TODO: customer -> prospect only by admins
    # TODO: lead -> prospect will lock and tag it to user who converts
    def convert_to_prospect(self, request, pk=None):
        user: UserProfile = request.user
        contact: Contact = self.get_object()
        controller = ContactLifecycleController(contact=contact)
        controller.update_lifecycle_status(user=user, status=Lifecycle.PROSPECT)
        return Response({"message": "Converted to prospect"}, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=["post"])
    def add_note(self, request: Request, pk=None):
        contact: Contact = self.get_object()
        note = ContactNote()
        note.tenant = contact.tenant
        note.contact = contact
        note.body = request.data.get("note")
        note.save()
        return Response({"message": "Added note"})

    # TODO: Add pagination?
    @action(detail=True, methods=["get"])
    def timeline(self, request: Request, pk=None):
        contact: Contact = self.get_object()
        timeline = contact.timeline.all().order_by("-created_on")
        data = [ContactTimelineSerializer(event).data for event in timeline]
        return Response(data)

    # TODO: Add pagination?
    @action(detail=True, methods=["get"])
    def notes(self, request: Request, pk=None):
        contact: Contact = self.get_object()
        notes = contact.notes.all().order_by("-created_on")
        data = [ContactNoteSerializer(note).data for note in notes]
        return Response(data)

    @action(detail=False, methods=["get"])
    def my_customers(self, request: Request, pk=None):
        user: UserProfile = request.user
        queryset = user.my_customers.all().order_by("name")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ContactListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ContactListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def my_prospects(self, request: Request, pk=None):
        user: UserProfile = request.user
        queryset = user.locked_contacts.all().order_by("name")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ContactListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = ContactListSerializer(queryset, many=True)
        return Response(serializer.data)
