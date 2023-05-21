from django.contrib import admin

from apps.contacts.models import Contact, ContactAssociate

admin.site.register(Contact)
admin.site.register(ContactAssociate)
