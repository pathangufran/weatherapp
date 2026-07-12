import logging
from alerts.models import WeatherAlert,AlertNotification

logger = logging.getLogger(__name__)

class NotificationRepository:

    @staticmethod
    def notification_exists(alert,weather_record):

        return AlertNotification.objects.filter(
            alert=alert,
            weather_record=weather_record
        ).exists()

    @staticmethod
    def create_notification(alert,weather_record,message):

        if NotificationService.notification_exists(
            alert,
            weather_record
        ):
            logger.info(
                "Notification already exists. "
                "Alert=%s",
                alert.id,
            )

            return None
        
        notification = AlertNotification.objects.create(
            alert=alert,
            weather_record=weather_record,
            message=message
        )

        logger.info(
            "Notification created successfully. "
            "Notification=%s",
            notification.id,

        )
        return notification