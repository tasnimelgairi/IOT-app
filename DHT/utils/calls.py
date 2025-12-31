import os
from django.conf import settings
from twilio.rest import Client
from twilio.http.http_client import TwilioHttpClient

def make_voice_call():
    if not getattr(settings, "ENABLE_CALL", False):
        return

    # Proxy PythonAnywhere (free)
    proxy_client = TwilioHttpClient(
        proxy={
            "http": os.environ.get("http_proxy"),
            "https": os.environ.get("https_proxy"),
        }
    )

    client = Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN,
        http_client=proxy_client
    )

    twiml_url = "https://tasnimelg.pythonanywhere.com/twiml/alert/"

    client.calls.create(
        to=settings.ALERT_CALL_TO,         # ex: +2126...
        from_=settings.TWILIO_CALL_FROM,   # ton numéro Twilio VOICE
        url=twiml_url
    )
