import logging
from django.core.cache import cache
from django_redis import get_redis_connection

logger = logging.getLogger(__name__)

class AlertRedisService:

    CACHE_VERSION = "v1"
    ALERT_TTL = 600
    NOTIFICATION_TTL = 300
    UNREAD_COUNT_TTL = 1800

    @classmethod
    def get_alert_key(cls,prefix,user_id,suffix=""):
        
        key = f"{prefix}:{cls.CACHE_VERSION}:user:{user_id}"

        if suffix:
            key = f"{key}:{suffix}"

        return key

    @classmethod
    def get_alert_data(cls,key):

        data = cache.get(key)
        if data:
            logger.info("Redis Cache HIT : %s",key)
        else:
            logger.info("Redis Cache MISS : %s",key)

        return data
    
    @classmethod
    def set_alert_data(cls,key,data):
        
        cache.set(
            key,
            data,
            timeout=cls.ALERT_TTL
        )
        logger.info("Redis Cache SET : %s",key)

    @classmethod
    def delete_alert_data(cls,key):

        cache.delete(key)
        logger.info("Redis Cache DELETE : %s",key)

    @classmethod
    def delete_alert_pattern(cls,key,pattern):

        connection = get_redis_connection("default")

        deleted = 0

        for key in connection.scan_iter(pattern):
            connection.delete(key)
            deleted += 1

        logger.info(
            "Deleted %s cache keys using pattern %s",
            deleted,
            pattern,
        )
