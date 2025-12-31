from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from django.core.mail import send_mail
from django.conf import settings

from .models import Dht11
from .utils.whatsapp import send_whatsapp_alert

# ================== SEUILS ==================
SEUIL_TEMP = 8.0
SEUIL_HUM  = 80.0

# ================== TWILIO (SAFE IMPORT) ==================
try:
    from twilio.base.exceptions import TwilioRestException
except Exception:
    TwilioRestException = Exception  # ✅ si Twilio non installé, Django ne plante pas


def notify(subject: str, message: str):
    print("🚀 notify() APPELÉ")   # 👈 ajoute cette ligne

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=settings.ALERT_EMAILS,
            fail_silently=False
        )
        print("📧 Email envoyé")
    except Exception as e:
        print("❌ Erreur Email:", e)

    if getattr(settings, "ENABLE_WHATSAPP", False):
        try:
            send_whatsapp_alert(message)
            print("📱 WhatsApp envoyé")
        except Exception as e:
            print("⚠️ WhatsApp ignoré:", e)

@api_view(["GET", "POST"])
def dht_list(request):

    # ================== GET ==================
    if request.method == "GET":
        data = Dht11.objects.all().order_by("-created_at")  # ✅ created_at

        result = []
        for obj in data:
            result.append({
                "id": obj.id,
                "temp": obj.temp,
                "hum": obj.hum,
                "created_at": obj.created_at,  # ✅ created_at
            })
        return Response(result, status=status.HTTP_200_OK)

    # ================== POST ==================
    if request.method == "POST":
        print("📥 Données reçues :", request.data)

        temp = request.data.get("temp")
        hum  = request.data.get("hum")

        if temp is None or hum is None:
            return Response(
                {"detail": "Champs 'temp' et 'hum' obligatoires"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ conversion sécurisée
        try:
            temp_val = float(temp)
            hum_val  = float(hum)
        except ValueError:
            return Response(
                {"detail": "temp et hum doivent être numériques"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ✅ ALERTES
        if temp_val > SEUIL_TEMP:
            msg = (
                f"🚨 ALERTE TEMPÉRATURE\n"
                f"Température = {temp_val}°C\n"
                f"Seuil = {SEUIL_TEMP}°C\n"
                f"Capteur : DHT11"
            )
            notify("🚨 ALERTE TEMPÉRATURE", msg)

        if hum_val > SEUIL_HUM:
            msg = (
                f"🚨 ALERTE HUMIDITÉ\n"
                f"Humidité = {hum_val}%\n"
                f"Seuil = {SEUIL_HUM}%\n"
                f"Capteur : DHT11"
            )
            notify("🚨 ALERTE HUMIDITÉ", msg)

        # ✅ Enregistrer
        obj = Dht11.objects.create(temp=temp_val, hum=hum_val)

        return Response(
            {
                "message": "Mesure enregistrée",
                "id": obj.id,
                "temp": obj.temp,
                "hum": obj.hum,
                "created_at": obj.created_at,  # ✅ created_at
            },
            status=status.HTTP_201_CREATED
        )

    return Response({"detail": "Méthode non autorisée"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
