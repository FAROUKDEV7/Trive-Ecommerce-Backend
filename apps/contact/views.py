from rest_framework import serializers, generics, permissions
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
import threading

from .models import ContactMessage


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'phone', 'subject', 'message', 'created_at']
        read_only_fields = ['id', 'created_at']


def _send_contact_email(subject, message, from_email, recipient_list):
    """Send email in background thread to avoid blocking the HTTP response."""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=True,
        )
    except Exception:
        pass


class ContactCreateView(generics.CreateAPIView):
    serializer_class = ContactSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()

        # Send email in background — does NOT block the HTTP response
        thread = threading.Thread(
            target=_send_contact_email,
            args=(
                f'New Contact: {obj.subject}',
                f'From: {obj.name} ({obj.email})\n\n{obj.message}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
            ),
            daemon=True,
        )
        thread.start()

        return Response({'success': True, 'message': 'Message sent successfully.'}, status=201)


class AdminContactListView(generics.ListAPIView):
    serializer_class = ContactSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = ContactMessage.objects.all()