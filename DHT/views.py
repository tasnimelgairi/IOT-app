import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render
from .models import Dht11
from django.shortcuts import render, redirect
from django.utils.dateparse import parse_date
from django.db.models import Avg
from django.db.models.functions import TruncDate
from django.utils import timezone
import csv
from django.http import HttpResponse


@csrf_exempt
@require_POST
def api_post(request):
    data = json.loads(request.body.decode())
    Dht11.objects.create(temp=data["temp"], hum=data["hum"])
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
    if not request.session.get("logged_in"):
        return redirect("/login/")

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

def home(request):
    return render(request, "home.html")

def login_view(request):
    error = False
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username == "tassnime.elgairi@gmail.com" and password == "admin":
            request.session["logged_in"] = True
            request.session["username"] = "admin"
            return redirect("dashboard")   # ✅ redirige vers /dashboard/
        else:
            error = True

    return render(request, "login.html", {"error": error})

def logout(request):
    return redirect("/login/")


def graphiqueTemp(request):
    if not request.session.get("logged_in"):
        return redirect("/login/")
    return render(request, 'ChartTemp.html')


def graphiqueHum(request):
    if not request.session.get("logged_in"):
        return redirect("/login/")
    return render(request, 'ChartHum.html')


from django.http import JsonResponse
from django.db.models import Avg
from django.db.models.functions import TruncDate
from datetime import datetime
from .models import Dht11

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

