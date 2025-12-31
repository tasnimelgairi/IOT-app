from twilio.rest import Client
from django.conf import settings

def send_whatsapp_alert(temp):
    client = Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN
    )

    message = (
        f"🚨 ALERTE TEMPÉRATURE 🚨\n"
        f"Température détectée : {temp}°C\n"
        f"Valeur hors plage autorisée (2°C – 8°C)\n"
        f"❄️ Vérifiez immédiatement le réfrigérateur."
    )

    client.messages.create(
        body=message,
        from_=settings.TWILIO_WHATSAPP_FROM,
        to=settings.ALERT_WHATSAPP_TO
    )
