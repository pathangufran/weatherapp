from django.urls import path
from weatherapp.views import *

urlpatterns = [
    path('weather/current',WeatherCurrent.as_view(),name='weather_current'),
    path('weather/latest',LatestWeather.as_view(),name='weather_latest'),
    path('weather/forecast',WeatherForecast.as_view(),name='weather_forecast'),
    path('weather/history',WeatherHistory.as_view(),name='weather_history'),
    path('weather/statistics',WeatherStatistics.as_view(),name='weather_statistics'),
    path('weather/compare',WeatherCompare.as_view(),name='weather_compare')
]