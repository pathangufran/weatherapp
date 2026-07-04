import logging
from celery import shared_task
from django.utils import timezone
from cities.models import City
from weatherapp.repository import WeatherRepository
from weatherapp.services import weather_data,WeatherServiceError

logger = logging.getLogger(__name__)

@shared_task
def test_task():

    current_time = timezone.now()

    logger.info(
        "Celery Beat executed at %s",
        current_time,
    )
    return (
        f"Executed Successfully at {current_time}"
    )

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3
)
def update_weather_data():

    logger.info(
        "Weather synchronization started."
    )
    success = 0
    failed = 0

    for city in City.objects.all():
        try:
            response = weather_data(city.id)
            current = response["current"]
            WeatherRepository.create(city.id,current)
            success += 1

        except WeatherServiceError as exc:
            failed += 1
            logger.exception(
                "Unexpected error for %s : %s",
                city.name,
                exc,
            )

    logger.info(
        "Weather synchronization completed. "
        "Success=%s Failed=%s",
        success,
        failed,

    )
    
    return {
        "success":success,
        "failed":failed
    }