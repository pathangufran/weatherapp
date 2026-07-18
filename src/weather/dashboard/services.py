from django.db.models import Count,Q,Avg,Min,Max
from alerts.models import WeatherAlert,AlertNotification
from cities.models import City,UserCity
from weatherapp.models import WeatherRecord
from datetime import timedelta
from django.utils import timezone
from django.db.models.functions import TruncDate
from alerts.models import WeatherAlert,AlertNotification
from itertools import chain

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

    @staticmethod
    def get_weather_trend(user,days):

        start_date = timezone.now() - timedelta(days=days)

        weather_trend = (
            WeatherRecord.objects.filter(
                city__city_users__user=user,
                created_at__gte=start_date
            )
            .annotate(
                date=TruncDate("created_at")
            )
            .values("date")
            .annotate(
                average_temperature=Avg("temperature"),
                average_humidity=Avg("humidity"),
                average_pressure=Avg("pressure"),
            )
            .order_by("date")
        )
        
        return list(weather_trend)
    
    @staticmethod
    def get_city_analytics(user):

        city_analytics = (

            City.objects.filter(city_user__user=user).annotate(
                weather_records=Count("weather_records"),
                average_temperature=Avg("weather_records__temperature"),
                highest_temperature=Max("weather_records__temperature"),
                lowest_temperature=Min("weather_records__temperature"),
                average_humidity=Avg("weather_records__humidity")
            )
            .values(
                "id",
                "name",
                "weather_records",
                "average_temperature",
                "highest_temperature",
                "lowest_temperature",
                "average_humidity"
            )
            .order_by("name")
        )
        
        return list(city_analytics)

    @staticmethod
    def get_alert_analytics(user):

        alert_analytics = (
            WeatherAlert.objects.filter(
                weather_alerts__user=user
            ).aggregate(
                total_alerts=Count("id"),
                active_alerts=Count("id",filter=Q(is_active=True)),
                inactive_alerts=Count("id",filter=Q(is_active=False)),
                triggered_alerts=Count("id",filter=Q(is_triggered=True)),
                temperature_alerts=Count("id",filter=Q(alert_type="tempature")),
                temperature_alerts=Count("id",filter=Q(alert_type="humidity")),
                temperature_alerts=Count("id",filter=Q(alert_type="wind_speed")),
                temperature_alerts=Count("id",filter=Q(alert_type="pressure"))
            )
        )

        return alert_analytics
    
    @staticmethod
    def get_notification_analytics(user):

        today = timezone.now().date()
        start = timezone.now() - timedelta(days=7)

        notification_analytics = (
            AlertNotification.objects.filter(alert__user=user).aggregate(
                total_notifications=Count("id"),
                read_notifications=Count("id",filter=Q(is_read=True)),
                unread_notifications=Count("id",filter=Q(is_read=False)),
                today_notifications=Count("id",filter=Q(created_at__date=today)),
                this_week_notifications=Count("id",filter=Q(created_at__gte=start))
            )
        )

        total = notification_analytics["total_notifications"] or 0
        read = notification_analytics["read_notifications"] or 0
        unread = notification_analytics["unread_notifications"] or 0

        if total > 0:
            notification_analytics["read_percentage"] = round(
                (read / total) * 100,2)
            notification_analytics["unread_percentage"] = round(
                (unread / total) * 100,2)
        else:
            notification_analytics["read_percentage"] = 0
            notification_analytics["unread_percentage"] = 0

        return notification_analytics
    
    @staticmethod
    def get_recent_activity(user,limit):

        weather_records = (
            WeatherRecord.objects.filter(
                city__city_users__user=user
            )
            .select_related("city")
            .only(
                "city__name",
                "temperature",
                "created_at",
            )
            .order_by("-created_at")[:limit]
        )

        weather_activity = []
        for record in weather_records:
            data = {
                "type": "weather",
                "title": "Weather Updated",
                "description": (
                    f"Latest weather synced for "
                    f"{record.city.name}."
                ),
                "city": record.city.name,
                "created_at": record.created_at,
            }
            weather_activity.append(data)

        alerts = (
            WeatherAlert.objects.filter(user=user)
            .select_related("city")
            .only(
                "city__name",
                "alert_type",
                "created_at",
            )
            .order_by("-created_at")[:limit]
        )

        alert_activity = []
        for alert in alerts:
            data = {
                "type": "alert",
                "title": f"{alert.alert_type.title()} Alert Created",
                "description": (
                    f"{alert.alert_type.title()} alert "
                    f"created for {alert.city.name}."
                ),
                "city": alert.city.name,
                "created_at": alert.created_at,
            }
            alert_activity.append(data)

        notifications = (
            AlertNotification.objects.filter(alert__user=user)
            .select_related("alert","alert__city")
            .only(
                "message",
                "created_at",
                "alert__city__name",
            )
            .order_by("-created_at")[:limit]
        )

        notification_activity = []
        for notification in notifications:
            data = {
                "type": "notification",
                "title": "Weather Alert Triggered",
                "description": notification.message,
                "city": notification.alert.city.name,
                "created_at": notification.created_at,
            }
            notification_activity.append(data)

        activity = list(
            chain(
                weather_activity,
                alert_activity,
                notification_activity,
            )
        )

        activity.sort(key=lambda item:item["created_at"],reverse=True)
        
        return activity[:limit]
        

