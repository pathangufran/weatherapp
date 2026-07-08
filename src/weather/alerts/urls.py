from django.urls import path
from alerts.views import CreateAlert,GetAlerts,AlertDetails

urlpatterns = [
    path('api/create',CreateAlert.as_view(),name='api_alerts'),
    path('api/get',GetAlerts.as_view(),name='api_get'),
    path('api/details',AlertDetails.as_view(),name='api_details')
]