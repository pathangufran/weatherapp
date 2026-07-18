from django.urls import path
from dashboard.views import DashboardSummary,DashboardWeatherAnalytics, \
                            WeatherTrends,DashboardCityAnalytics,DashboardAlertAnalytics,\
                            DashboardNotificationAnalytics
                            

urlpatterns = [
    path('',DashboardSummary.as_view(),name='dashboard_summary'),
    path('weather',DashboardWeatherAnalytics.as_view(),name='dashboard_weather_analytics'),
    path('weather/trends',WeatherTrends.as_view(),name='dashboard_weather_trends'),
    path('city/analytics',DashboardCityAnalytics.as_view(),name='dashboard_city_analytics'),
    path('alert/analytics',DashboardAlertAnalytics.as_view(),name='dashboard_alert_analytics'),
    path('notification/analytics',DashboardNotificationAnalytics.as_view(),name='dashboard_notification_analytics')

]