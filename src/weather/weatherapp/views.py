import logging
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from cities.models import City
from weatherapp.models import WeatherRecord
from services import *

logger = logging.getLogger(__name__)

class WeatherCurrent(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        city_id = request.data.get("city_id")
        if not city_id:
            return Response(
                {"message": "city_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        city = get_object_or_404(City, id=city_id)

        try:
            data = weather_data(city_id)
            current = data["current"]

            WeatherRecord.objects.create(
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

            logger.info("Weather record saved for %s", city.name)
            return Response(
                {"message": "Weather data added successfully."},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.exception("Unexpected Error: %s", e)
            return Response(
                {"message": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )