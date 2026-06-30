from django.urls import path
from weatherapp.views import *

urlpatterns = [
    path('weather/current',WeatherCurrent.as_view(),name='weather_current')    
]