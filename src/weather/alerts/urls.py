from django.urls import path
from alerts.views import CreateAlert,GetAlerts,AlertDetails, \
                        UpdateAlert,AlertStatus,DeleteAlert

urlpatterns = [
    path('api/create',CreateAlert.as_view(),name='api_alerts'),
    path('api/get',GetAlerts.as_view(),name='api_get'),
    path('api/details',AlertDetails.as_view(),name='api_details'),
    path('api/update',UpdateAlert.as_view(),name='api_update'),
    path('api/status',AlertStatus.as_view(),name='api_status'),
    path('api/delete',DeleteAlert.as_view(),name='api_delete')
]