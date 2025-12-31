from django.conf import settings
from django.core.mail import send_mail

def send_email_alert(subject: str, message: str, to_emails=None):
    if to_emails is None:
        to_emails = settings.ALERT_EMAILS

    if not to_emails:
        return  # pas de destinataires configurés

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        to_emails,
        fail_silently=False,
    )
