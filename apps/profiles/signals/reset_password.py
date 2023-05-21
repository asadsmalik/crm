from apps.utils.email import send_email
from django.dispatch import receiver
from django.urls import reverse
from django_rest_passwordreset.signals import reset_password_token_created


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):

    email_body = "{}?token={}".format(reverse('password_reset:reset-password-request'), reset_password_token.key)
    send_email({
        "email_subject": "Password Reset for {title}".format(title="ClowdLink"),
        "email_body": email_body,
        "to": [reset_password_token.user.email]
    })
