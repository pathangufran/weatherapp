from django.urls import path
from alerts.views import CreateAlert

urlpatterns = [
    path('api/alerts',CreateAlert.as_view(),name='api_alerts')
]