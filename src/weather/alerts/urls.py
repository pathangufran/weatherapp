from django.urls import path
from alerts.views import CreateAlert,GetAlerts,AlertDetails, \
                        UpdateAlert,AlertStatus,DeleteAlert,GetNotifications, \
                        NotificationDetails,NotificationRead,NotificationAllRead, \
                        NotificationDelete

urlpatterns = [
    path('api/create',CreateAlert.as_view(),name='api_alerts'),
    path('api/get',GetAlerts.as_view(),name='api_get'),
    path('api/details',AlertDetails.as_view(),name='api_details'),
    path('api/update',UpdateAlert.as_view(),name='api_update'),
    path('api/status',AlertStatus.as_view(),name='api_status'),
    path('api/delete',DeleteAlert.as_view(),name='api_delete'),
    path('api/notifications',GetNotifications.as_view(),name='api_notifications'),
    path('api/notification/details',NotificationDetails.as_view(),name='api_notification_details'),
    path('api/notification/read',NotificationRead.as_view(),name='api_notification_read'),
    path('api/notification/read/all',NotificationAllRead.as_view(),name='api_notification_read_all'),
    path('api/notification/delete',NotificationDelete.as_view(),name='api_notification_delete')
]