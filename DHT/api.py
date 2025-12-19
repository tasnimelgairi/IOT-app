from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Dht11

SEUIL_TEMP = 8
SEUIL_HUM = 80

@api_view(["GET", "POST"])
def dht_list(request):

    if request.method == "GET":
        data = Dht11.objects.all().order_by("-created_at")
        result = []

        for obj in data:
            result.append({
                "id": obj.id,
                "temp": obj.temp,
                "hum": obj.hum,
                "dt": obj.created_at,   # ✅ on garde la clé "dt" pour ton frontend si tu veux
            })

        return Response(result, status=status.HTTP_200_OK)

    if request.method == "POST":
        temp = request.data.get("temp")
        hum = request.data.get("hum")

        if temp is None or hum is None:
            return Response(
                {"detail": "Champs 'temp' et 'hum' obligatoires"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            temp_val = float(temp)
            hum_val = float(hum)
        except ValueError:
            return Response(
                {"detail": "Valeurs invalides pour temp ou hum"},
                status=status.HTTP_400_BAD_REQUEST
            )

        obj = Dht11.objects.create(temp=temp_val, hum=hum_val)

        return Response(
            {
                "message": "Mesure enregistrée",
                "id": obj.id,
                "temp": obj.temp,
                "hum": obj.hum,
                "dt": obj.created_at,   # ✅ pareil ici
            },
            status=status.HTTP_201_CREATED
        )
