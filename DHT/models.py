from django.db import models

class Dht11(models.Model):
    temp = models.FloatField()
    hum = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
