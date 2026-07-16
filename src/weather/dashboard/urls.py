from django.urls import path
from dashboard.views import DashboardSummary,DashboardWeatherAnalytics

urlpatterns = [
    path('',DashboardSummary.as_view(),name='dashboard_summary'),
    path('weather/',DashboardWeatherAnalytics.as_view(),name='dashboard_weather_analytics')
]