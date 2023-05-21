from rest_framework import serializers

from apps.contacts.models import Contact, ContactNote, ContactTimeline


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        read_only = ["created_by", "locked_by", "customer_of", "locked_on", "is_locked"]
        exclude = ["tenant"]

class ContactListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        read_only = ['created_by']
        fields = '__all__'

class ContactTimelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactTimeline
        read_only = ['created_on', 'title']
        fields = ['created_on', 'title']

class ContactNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactNote
        read_only = ['created_on', 'body']
        fields = ['created_on', 'body']
