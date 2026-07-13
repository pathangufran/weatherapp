

def notification_response(notification):

    return {
        "id": notification.id,
        "city": notification.alert.city.name,
        "message": notification.message,
        "is_read": notification.is_read,
        "created_at": notification.created_at,
        "weather": {
            "temperature": notification.weather_record.temperature,
            "humidity": notification.weather_record.humidity,
            "pressure": notification.weather_record.pressure,
            "wind_speed": notification.weather_record.wind_speed,
            "condition": notification.weather_record.weather,
        }
    }