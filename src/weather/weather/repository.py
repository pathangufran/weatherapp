import logging
from weatherapp.models import WeatherRecord
from weather.redis_service import RedisService

logger = logging.getLogger(__name__)

class WeatherRepository:

    @staticmethod
    def create(city,current):

        weather = WeatherRecord.objects.create(
            city=city,
            temperature=current["temp_c"],
            feels_like=current["feelslike_c"],
            humidity=current["humidity"],
            pressure=current["pressure_mb"],
            wind_speed=current["wind_kph"],
            wind_direction=current["wind_degree"],
            visibility=current["vis_km"],
            uv_index=current["uv"],
            weather=current["condition"]["text"],
            weather_code=current["condition"]["code"],
            icon=current["condition"]["icon"],
        )
        response = {
            "city": city.name,
            "temperature": float(weather.temperature),
            "feels_like": float(weather.feels_like),
            "humidity": weather.humidity,
            "pressure": weather.pressure,
            "wind_speed": float(weather.wind_speed),
            "wind_direction": weather.wind_direction,
            "visibility": weather.visibility,
            "uv_index": float(weather.uv_index),
            "condition": weather.weather,
            "weather_code": weather.weather_code,
            "icon": weather.icon,
            "recorded_at": weather.recorded_at.isoformat(),
        }
        
        RedisService.refresh_weather(city.id,response)
        RedisService.delete_weather_statistics(city.id)
        
        logger.info(
            "Weather stored successfully for %s",
            city.name
        )
        return weather
    