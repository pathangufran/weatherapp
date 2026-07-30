from django.urls import path
from common.health.views import HealthCheck,DetailedHealthCheck

urlpatterns = [
    path('',HealthCheck.as_view(),name='health'),
    path('detailed/',DetailedHealthCheck.as_view(),name='health_detailed')
]