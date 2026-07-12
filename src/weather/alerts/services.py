import logging
from alerts.models import WeatherAlert
from alerts.repository import NotificationRepository

logger = logging.getLogger(__name__)

class AlertService:

    @staticmethod
    def get_weather_value(alert_type,weather_record):

        mapping = {
            "temperature": weather_record.temperature,
            "humidity": weather_record.humidity,
            "pressure": weather_record.pressure,
            "wind_speed": weather_record.wind_speed,
            "uv_index": weather_record.uv_index,
            "condition": weather_record.weather,
        }
        return mapping.get(alert_type)
    
    @staticmethod
    def compare(current,operator,threshold):

        try:
            if operator == "eq":
                return str(current).lower() == str(threshold).lower()
            
            current = float(current)
            threshold = float(threshold)

            if operator == "gt":
                return current > threshold
        
            if operator == "gte":
                return current >= threshold
            
            if operator == "lt":
                return current < threshold
            
            if operator == "lte":
                return current <= threshold
        
        except Exception:
            logger.exception("Comparison failed.")

        return False
    
    @staticmethod
    def handle_trigger(alert,weather_record,value):

        if alert.is_triggered:
            logger.info(
                "Alert %s already triggered.",
                alert.id,
            )
            return
        
        message = (
            f"{alert.city.name}: "
            f"{alert.alert_type} "
            f"{value} "
            f"matched alert "
            f"{alert.operator} "
            f"{alert.threshold}"
        )

        NotificationRepository.create_notification(
            alert=alert,
            weather_record=weather_record,
            message=message
        )
        
        alert.is_triggered = True

        alert.save(update_fields=["is_triggered"])

        logger.info("Alert %s triggered.",alert.id)

    @staticmethod
    def reset_trigger(alert):

        if not alert.is_triggered:
            return
        
        alert.is_triggered = False

        alert.save(update_fields=["is_triggered"])

        logger.info("Alert %s reset.",alert.id)

    @staticmethod
    def evaluate_alert(alert,weather_record):

        current_value = AlertService.get_weather_value(
            alert.alert_type,
            weather_record,
        )
        if current_value is None:
            logger.warning(
                "Unsupported alert type %s",
                alert.alert_type,
            )

            return
        
        condition = AlertService.compare(
            current_value,
            alert.operator,
            alert.threshold,
        )
        if condition:
            AlertService.handle_trigger(alert,weather_record,current_value)
        else:
            AlertService.reset_trigger(alert)

    @staticmethod
    def process_alerts(weather_record):

        logger.info(
            "Processing alerts for city %s",
            weather_record.city.name,
        )
        alerts = (
            WeatherAlert.objects.filter(
                city=weather_record.city,
                is_active=True
            ).select_related("user","city")
        )
        
        for alert in alerts:
            AlertService.evaluate_alert(
                alert,
                weather_record,
            )