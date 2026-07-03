import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

class RedisService:
    
    CACHE_VERSION = "v1"
    CURRENT_WEATHER_TTL = 600
    LATEST_WEATHER_TTL = 600
    FORECAST_WEATHER_TTL = 600
    STATISTICS_WEATHER_TTL = 600
    HISTORY_WEATHER_TTL = 600

    @classmethod
    def current_weather_key(cls,city_id):
        return f"weather:{cls.CACHE_VERSION}:current:{city_id}"
    
    @classmethod
    def latest_weather_key(cls,city_id):
        return f"weather:{cls.CACHE_VERSION}:latest:{city_id}"
    
    @classmethod
    def weather_forecast_key(cls,city_id):
        return f"weather:{cls.CACHE_VERSION}:forecast:{city_id}"
    
    @classmethod
    def weather_statistics_key(cls,city_id):
        return f"weather:{cls.CACHE_VERSION}:statistics:{city_id}"

    @classmethod
    def weather_history_key(cls,city_id,page,limit,start_date,end_date):
        start_date = start_date or "none"
        end_date = end_date or "none"
        return (
            f"weather:{cls.CACHE_VERSION}:history:"
            f"{city_id}:{page}:{limit}:{start_date}:{end_date}"
        )
    

    @classmethod
    def get_current_weather(cls,city_id):
        
        key = cls.current_weather_key(city_id)
        data = cache.get(key)
        if data:
            logger.info("CACHE HIT : %s", key)
        else:
            logger.info("CACHE MISS : %s", key)

        return data
    
    @classmethod
    def set_current_weather(cls,city_id,data):
        
        key = cls.current_weather_key(city_id)
        cache.set(
            key,
            data,
            timeout=cls.CURRENT_WEATHER_TTL
        )
        logger.info("CACHE SET : %s", key)

    @classmethod
    def delete_current_weather(cls,city_id):
        
        key = cls.current_weather_key(city_id)
        cache.delete(key)
        logger.info("CACHE DELETE : %s", key)

    @classmethod
    def get_latest_weather(cls,city_id):
        
        key = cls.latest_weather_key(city_id)
        data = cache.get(key)
        if data:
            logger.info("CACHE HIT : %s", key)
        else:
            logger.info("CACHE MISS : %s", key)

        return data
    
    @classmethod
    def set_latest_weather(cls,city_id,data):
        
        key = cls.latest_weather_key(city_id)
        cache.set(
            key,
            data,
            timeout=cls.LATEST_WEATHER_TTL
        )
        logger.info("CACHE SET : %s", key)

    @classmethod
    def delete_latest_weather(cls,city_id):
        
        key = cls.latest_weather_key(city_id)
        cache.delete(key)
        logger.info("CACHE DELETE : %s", key)

    @classmethod
    def get_weather_statistics(cls,city_id):

        key = cls.weather_statistics_key(city_id)
        data = cache.get(key)
        if data:
            logger.info("CACHE HIT : %s", key)
        else:
            logger.info("CACHE MISS : %s", key)

        return data
    
    @classmethod
    def set_weather_statistics(cls,city_id,data):
        
        key = cls.weather_statistics_key(city_id)
        cache.set(
            key,
            data,
            timeout=cls.STATISTICS_WEATHER_TTL
        )
        logger.info("CACHE SET : %s", key)

    @classmethod
    def delete_weather_statistics(cls,city_id):

        key = cls.weather_statistics_key(city_id)
        cache.delete(key)
        logger.info("CACHE DELETED : %s", key)

    @classmethod
    def get_weather_forecast(cls,city_id):
        
        key = cls.weather_forecast_key(city_id)
        data = cache.get(key)
        if data:
            logger.info("CACHE HIT : %s", key)
        else:
            logger.info("CACHE MISS : %s", key)

        return data
    
    @classmethod
    def set_weather_forecast(cls,city_id,data):
        
        key = cls.weather_forecast_key(city_id)
        cache.set(
            key,
            data,
            timeout=cls.FORECAST_WEATHER_TTL
        )
        logger.info("CACHE SET : %s", key)

    @classmethod
    def delete_weather_forecast(cls,city_id):
        
        key = cls.weather_forecast_key(city_id)
        cache.delete(key)
        logger.info("CACHE DELETED : %s", key)

    @classmethod
    def get_weather_history(cls,city_id,page,limit,start_date,end_date):
        
        key = cls.weather_history_key(city_id,page,limit,start_date,end_date)
        data = cache.get(key)
        if data:
            logger.info("CACHE HIT : %s", key)
        else:
            logger.info("CACHE MISS : %s", key)

        return data
    
    @classmethod
    def set_weather_history(cls,city_id,page,limit,start_date,end_date,data):

        key = cls.weather_history_key(city_id,page,limit,start_date,end_date)
        cache.set(
            key,
            data,
            timeout=cls.HISTORY_WEATHER_TTL
        )
        logger.info("CACHE SET : %s", key)

    @classmethod
    def delete_weather_history(cls,city_id):

        from django_redis import get_redis_connection

        connection = get_redis_connection("default")
        pattern = (
            f"weather:{cls.CACHE_VERSION}:history:{city_id}:*"
        )
        for key in connection.scan_iter(pattern):
            connection.delete(key)

        logger.info(
            "History cache deleted for city %s",
            city_id
        )

    @classmethod
    def refresh_weather(cls,city_id,data):

        cls.set_current_weather(city_id,data)
        cls.set_latest_weather(city_id,data)

    @classmethod
    def invalidate_weather(cls, city_id):

        cls.delete_current_weather(city_id)
        cls.delete_latest_weather(city_id)

