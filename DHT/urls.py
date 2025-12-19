from django.urls import path
from .views import home, dashboard, api_post, login_view, json_view, logout, chart_data_mois, graphiqueTemp, graphiqueHum, chart_data, download_csv
from . import api

urlpatterns = [
    path("", home, name="home"),
    path("login/", login_view, name="login"),
    path("logout/", logout, name="logout"),

    path("dashboard/", dashboard, name="dashboard"),
    path("api/post/", api_post, name="api_post"),
    path("json/", json_view, name="json"),
    path("api", api.dht_list, name='json'),

    path('myChartTemp/', graphiqueTemp, name='myChartTemp'),
    path('myChartHum/', graphiqueHum, name='myChartHum'),
    path('chart-data/', chart_data, name='chart-data'),
    path("chart-data-mois/", chart_data_mois, name="chart_data_mois"),
    path('download-csv/', download_csv, name='download_csv'),
]
