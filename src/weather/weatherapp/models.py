from django.db import models
from cities.models import *

class WeatherRecord(models.Model):

    id = models.AutoField(primary_key=True)
    city = models.ForeignKey(City,on_delete=models.CASCADE,related_name='city_weather')
    temperature = models.DecimalField(max_digits=5, decimal_places=2)
    feels_like = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    humidity = models.IntegerField(null=True, blank=True)
    pressure = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    wind_speed = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    wind_direction = models.IntegerField(null=True, blank=True)
    visibility = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    uv_index = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    weather = models.CharField(max_length=100, null=True, blank=True)
    weather_code = models.IntegerField(null=True, blank=True)
    icon = models.CharField(max_length=255, null=True, blank=True)
    sunrise = models.TimeField(null=True, blank=True)
    sunset = models.TimeField(null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True,db_index=True)

    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['recorded_at'])
        ]

    def __str__(self):
        
        return f'{self.city} - {self.temperature}°C at {self.recorded_at}'