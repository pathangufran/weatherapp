from django.urls import path
from common.health.views import HealthCheck

urlpatterns = [
    path('',HealthCheck.as_view(),name='health')
]