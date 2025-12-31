from django.db import models
from django.contrib.auth.models import User

class Dht11(models.Model):
    temp = models.FloatField()
    hum = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cin = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
