import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_date
from django.db.models import Avg
from django.db.models.functions import TruncDate
from django.utils import timezone
import csv
from django.http import HttpResponse
from .utils.whatsapp import send_whatsapp_alert
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Profile, Dht11
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.utils.dateparse import parse_date
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.db.models import Avg
from django.db.models.functions import TruncDate
from .models import Dht11
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from .models import Dht11
from DHT.utils.alerts import send_email_alert


TEMP_MAX = 8.0
TEMP_MIN = 2.0
HUM_MAX  = 80.0

@csrf_exempt
@require_POST
def api_post(request):
    data = json.loads(request.body.decode())

    temp_val = float(data["temp"])
    hum_val  = float(data["hum"])

    # Enregistrer la mesure
    obj = Dht11.objects.create(temp=temp_val, hum=hum_val)

    # 🚨 Condition d'alerte
    if temp_val > TEMP_MAX or temp_val < TEMP_MIN or hum_val > HUM_MAX:
        subject = "🚨 Alerte Cold Chain - Seuil dépassé"
        message = (
            f"Une mesure hors seuil a été détectée.\n\n"
            f"Température : {temp_val} °C\n"
            f"Humidité : {hum_val} %\n"
            f"Date : {obj.created_at}\n"
            f"Site : tasnimelg.pythonanywhere.com"
        )
        send_email_alert(subject, message)
        send_whatsapp_alert(temp_val)

    return JsonResponse({"ok": True})



def json_view(request):
    data = list(
        Dht11.objects.values(
            "id",
            "temp",
            "hum",
            "created_at"
        )
    )
    return JsonResponse(data, safe=False)


def dashboard(request):

    derniere = Dht11.objects.order_by('-created_at').first()

    if derniere:
        valeurs = {
            "temp": derniere.temp,
            "hum": derniere.hum,
            "date": derniere.created_at.strftime("%d/%m/%Y %H:%M:%S")
        }
    else:
        valeurs = {
            "temp": "--",
            "hum": "--",
            "date": "--"
        }

    return render(request, "dashboard.html", {"valeurs": valeurs})



def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        confirm  = request.POST.get("confirm_password", "")

        # Vérifications
        if not username or not password:
            return render(request, "register.html", {
                "error": "Tous les champs sont obligatoires."
            })

        if password != confirm:
            return render(request, "register.html", {
                "error": "Les mots de passe ne correspondent pas."
            })

        if User.objects.filter(username=username).exists():
            return render(request, "register.html", {
                "error": "Ce nom d’utilisateur existe déjà."
            })

        # Création user (mot de passe HASHÉ automatiquement)
        User.objects.create_user(
            username=username,
            password=password
        )

        return redirect("login")

    return render(request, "register.html")



def gestInsident(request):

    start = request.GET.get("start")  # "YYYY-MM-DD"
    end   = request.GET.get("end")    # "YYYY-MM-DD"

    qs = Dht11.objects.all().order_by("-created_at")

    d1 = parse_date(start) if start else None
    d2 = parse_date(end) if end else None

    if d1:
        qs = qs.filter(created_at__date__gte=d1)
    if d2:
        qs = qs.filter(created_at__date__lte=d2)

    rows = []
    for m in qs:
        dt = timezone.localtime(m.created_at)
        temp = float(m.temp)

        is_normal = (temp > 2) and (temp < 8)

        rows.append({
            "date": dt.strftime("%d/%m/%Y"),
            "heure": dt.strftime("%H:%M:%S"),
            "temp": temp,
            "hum": m.hum,
            "normal": is_normal,
            "anormal": not is_normal,
        })

    return render(request, "gestInsident.html", {
        "rows": rows,
        "start": start or "",
        "end": end or "",
    })

def test_temp_hum(request):
    result = None

    if request.method == "POST":
        temp = request.POST.get("temp")
        hum  = request.POST.get("hum")

        try:
            temp = float(temp)
            hum  = float(hum)

            is_normal = (temp > 2) and (temp < 8)
            result = {
                "temp": temp,
                "hum": hum,
                "normal": is_normal
            }

            # ✅ si tu veux ENREGISTRER dans la BD (sinon supprime cette ligne)
            Dht11.objects.create(temp=temp, hum=hum)

        except:
            result = {"error": "Valeurs invalides"}

    return render(request, "test_temp_hum.html", {"result": result})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "dashboard.html", {
                "error": True
            })

    return render(request, "login.html")


def home(request):

    return render(request, "home.html")


def logout(request):
    return redirect("/")

def graphiqueTemp(request):

    return render(request, 'ChartTemp.html')


def graphiqueHum(request):

    return render(request, 'ChartHum.html')



def chart_data_mois(request):
    start = request.GET.get("start")
    end   = request.GET.get("end")

    qs = Dht11.objects.all()

    # ✅ filtre sur created_at (pas dt)
    if start:
        qs = qs.filter(created_at__date__gte=start)  # start = "YYYY-MM-DD"
    if end:
        qs = qs.filter(created_at__date__lte=end)

    # ✅ regrouper par jour
    qs = (
        qs.annotate(day=TruncDate("created_at"))
          .values("day")
          .annotate(
              avg_temp=Avg("temp"),
              avg_hum=Avg("hum")
          )
          .order_by("day")
    )

    temps = [x["day"].strftime("%d/%m") for x in qs]
    temperature = [round(x["avg_temp"] or 0, 2) for x in qs]
    humidity = [round(x["avg_hum"] or 0, 2) for x in qs]

    return JsonResponse({
        "temps": temps,
        "temperature": temperature,
        "humidity": humidity,   # ✅ clé attendue par la page HUM
    })


def chart_data(request):
    dht = Dht11.objects.all()
    return JsonResponse({
        'temps': [d.created_at.strftime("%Y-%m-%d %H:%M") for d in dht],
        'temperature': [d.temp for d in dht],
        'humidity': [d.hum for d in dht]
    })



def download_csv(request):
    model_values = Dht11.objects.all().order_by("created_at")

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="dht.csv"'

    writer = csv.writer(response)

    # En-têtes CSV
    writer.writerow(['id', 'temp', 'hum', 'created_at'])

    # Données
    liste = model_values.values_list('id', 'temp', 'hum', 'created_at')
    for row in liste:
        writer.writerow(row)

    return response



@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_post(request):
    # ✅ GET : retourner les 100 dernières mesures
    if request.method == "GET":
        dht = Dht11.objects.all().order_by("-created_at")[:100]
        data = [
            {
                "id": m.id,
                "temp": m.temp,
                "hum": m.hum,
                "created_at": m.created_at.isoformat()
            }
            for m in dht
        ]
        return JsonResponse(data, safe=False)

    # ✅ POST : recevoir ESP et enregistrer
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "JSON invalide"}, status=400)

    temp = data.get("temp")
    hum  = data.get("hum")

    if temp is None or hum is None:
        return JsonResponse({"error": "Champs 'temp' et 'hum' obligatoires"}, status=400)

    try:
        temp_val = float(temp)
        hum_val  = float(hum)
    except ValueError:
        return JsonResponse({"error": "temp/hum doivent être numériques"}, status=400)

    # ✅ Enregistrer la mesure
    obj = Dht11.objects.create(temp=temp_val, hum=hum_val)

    # ✅ Alerte si hors seuil
    if temp_val > TEMP_MAX or temp_val < TEMP_MIN or hum_val > HUM_MAX:
        subject = "🚨 Alerte Cold Chain - Seuil dépassé"
        message = (
            f"Une mesure hors seuil a été détectée.\n\n"
            f"Température : {temp_val} °C\n"
            f"Humidité : {hum_val} %\n"
            f"Date : {obj.created_at.strftime('%d/%m/%Y %H:%M:%S')}\n"
        )
        send_email_alert(subject, message)

    return JsonResponse(
        {
            "ok": True,
            "id": obj.id,
            "temp": obj.temp,
            "hum": obj.hum,
            "created_at": obj.created_at.isoformat(),
        },
        status=201
    )

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def twiml_alert(request):
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say language="fr-FR" voice="alice">
    Alerte Cold Chain. Température hors seuil. Veuillez vérifier le réfrigérateur immédiatement.
  </Say>
</Response>"""
    return HttpResponse(xml, content_type="text/xml")
