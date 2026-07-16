from django.db.models import Count,Q,Avg,Min,Max
from alerts.models import WeatherAlert,AlertNotification
from cities.models import UserCity
from weatherapp.models import WeatherRecord

class DashboardService:

    @staticmethod
    def get_dashboard_summary(user):

        tracked_cities = UserCity.objects.filter(user=user).count()

        weather_records = WeatherRecord.objects.filter(
            city__city_users__user=user
        ).count()

        alerts = WeatherAlert.objects.filter(user=user).aggregate(
            active_alerts=Count(
                "id",
                filter=Q(is_active=True),
            ),
            inactive_alerts=Count(
                "id",
                filter=Q(is_active=True),
            ),
            triggered_alerts=Count(
                "id",
                filter=Q(is_triggered=True),
            ),
        )

        notifications = AlertNotification.objects.filter(
            alert__user=user
        ).aggregate(
            total_notifications=Count("id"),
            unread_notifications=Count(
                "id",
                filter=Q(is_read=False),
            ),
        )
        return {
            "tracked_cities": tracked_cities,
            "weather_records": weather_records,
            "active_alerts": alerts["active_alerts"],
            "inactive_alerts": alerts["inactive_alerts"],
            "triggered_alerts": alerts["triggered_alerts"],
            "notifications": notifications["total_notifications"],
            "unread_notifications": notifications["unread_notifications"],

        }
    
    @staticmethod
    def get_weather_analytics(user):

        analytics = (
            WeatherRecord.objects.filter(
                city__city_user__user=user
            )
            .aggregate(
                average_temperature=Avg("temperature"),
                highest_temperature=Max("temperature"),
                lowest_temperature=Min("temperature"),
                average_humidity=Avg("humidity"),
                highest_humidity=Max("humidity"),
                lowest_humidity=Min("humidity"),
                average_pressure=Avg("pressure"),
                average_wind_speed=Avg("wind_speed"),
                average_visibility=Avg("visibility"),
                average_uv_index=Avg("uv_index"),
            )
        )

        return analytics
