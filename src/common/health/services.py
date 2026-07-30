from django.db import connection
from django_redis import get_redis_connection
from weather.weather.celery import app

class HealthService:

    @staticmethod
    def check_database():

        """
        Returns True if PostgreSQL is reachable.
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

            return True
        
        except Exception:
            return False

    @staticmethod
    def check_redis():

        """
        Returns True if Redis is reachable.
        """
        try:
            redis = get_redis_connection("default")
            redis.ping()
            return True
        
        except Exception:
            return False

    @staticmethod
    def check_celery():

        """
        Returns True if Celery broker is reachable.
        """
        try:
            with app.connection_for_read() as connection:
                connection.ensure_connection(max_retries=1)
            return True
        
        except Exception:
            return False

    @classmethod
    def get_healthy_status(cls):

        database = cls.check_database()
        redis = cls.check_redis()
        celery = cls.check_celery()

        checks = {
            "application": "healthy",
            "database": "healthy" if database else "unhealthy",
            "redis": "healthy" if redis else "unhealthy",
            "celery": "healthy" if celery else "unhealthy",
        }

        overall = (
            "healthy"
            if database and redis and celery
            else "unhealthy"
        )

        return overall,checks
    