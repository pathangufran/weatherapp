import logging
from datetime import datetime
from cities.models import City
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from weatherapp.models import WeatherRecord
from weatherapp.services import *
from django.core.paginator import Paginator,EmptyPage

logger = logging.getLogger(__name__)

class WeatherCurrent(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        city_id = request.data.get("city_id")
        if not UserCity.objects.filter(user=request.user,city_id=city_id).exists():
            return Response(
                {'message':'You are not tracking this city.'},
                status=status.HTTP_403_FORBIDDEN
            )

        city = get_object_or_404(City, id=city_id)

        try:
            data = weather_data(city_id)
            current = data["current"]

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

            logger.info("Weather record saved for %s", city.name)
            return Response(
                {
                    "message": "Weather fetched successfully",
                    "data": {
                        "city": city.name,
                        "temperature": weather.temperature,
                        "feels_like": weather.feels_like,
                        "humidity": weather.humidity,
                        "pressure": weather.pressure,
                        "wind_speed": weather.wind_speed,
                        "wind_direction": weather.wind_direction,
                        "visibility": weather.visibility,
                        "uv_index": weather.uv_index,
                        "condition": weather.weather,
                        "icon": weather.icon,
                        "recorded_at": weather.recorded_at,
                    }
                },
                status=status.HTTP_200_OK,
            )
        
        except WeatherServiceError as e:
            logger.error(str(e))
            return Response(
                {"message": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        except Exception as e:
            logger.exception("Unexpected Error: %s", e)
            return Response(
                {"message": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
class LatestWeather(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):

        city_id = request.query_params.get('city_id')
        if not UserCity.objects.filter(user=request.user,city_id=city_id).exists():
            return Response(
                {"message": "You are not tracking this city."},
                status=status.HTTP_403_FORBIDDEN,
            )
        city = get_object_or_404(City,id=city_id)
        weather = WeatherRecord.objects.get(city=city)
        if not weather:
            return Response(
                {'message':'No weather record found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(
            {
                "city": city.name,
                "temperature": weather.temperature,
                "feels_like": weather.feels_like,
                "humidity": weather.humidity,
                "pressure": weather.pressure,
                "wind_speed": weather.wind_speed,
                "wind_direction": weather.wind_direction,
                "visibility": weather.visibility,
                "uv_index": weather.uv_index,
                "condition": weather.weather,
                "icon": weather.icon,
                "recorded_at": weather.recorded_at,
            }
        )
    
class WeatherForecast(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        city_id = request.data.get("city_id")
        if not UserCity.objects.filter(user=request.user,city_id=city_id).exists():
            return Response(
                {'message':'You are not tracking this city.'},
                status=status.HTTP_403_FORBIDDEN
            )

        city = get_object_or_404(City, id=city_id)

        try:
            data = forecast_data(city_id)
            
            logger.info("Weather record saved for %s", city.name)
            return Response(
                {"message": "Weather fetched successfully","data": data},
                status=status.HTTP_200_OK,
            )
        
        except WeatherServiceError as e:
            logger.error(str(e))
            return Response(
                {"message": str(e)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        except Exception as e:
            logger.exception("Unexpected Error: %s", e)
            return Response(
                {"message": "Something went wrong."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class WeatherHistory(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):

        city_id = request.query_params.get('city_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if not UserCity.objects.filter(user=request.user,city_id=city_id).exists():
            logger.warning(
                "%s tried to access city %s",
                request.user.username,
                city_id
            )
            return Response(
                {"message": "You are not tracking this city."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        city = get_object_or_404(City,id=city_id)
        weather_set = WeatherRecord.objects.filter(city=city).order_by('-recorded_at')
        filter = {}
        try:
            if start_date:
                filter['recorded_at__gte':start_date]
            if end_date:
                filter['recorded_at__lte':end_date]

        except ValueError:
            return Response(
                {"message":"Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST
            )
        weather_set = weather_set.filter(**filter)
        page = int(request.query_params.get('page',1))
        limit = int(request.query_params.get('limit',10))
        paginator = Paginator(weather_set,limit)
        try:
            weather_page = paginator.page(page)
        except EmptyPage:
            return Response(
                {"message": "Page not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        history = []

        for weather in weather_page:
            data = {
                "id": weather.id,
                "temperature": weather.temperature,
                "feels_like": weather.feels_like,
                "humidity": weather.humidity,
                "pressure": weather.pressure,
                "wind_speed": weather.wind_speed,
                "wind_direction": weather.wind_direction,
                "visibility": weather.visibility,
                "uv_index": weather.uv_index,
                "condition": weather.weather,
                "weather_code": weather.weather_code,
                "icon": weather.icon,
                "recorded_at": weather.recorded_at,
            }
            history.append(data)

        logger.info(
            "Weather history fetched for %s",
            city.name
        )
        return Response(
            {
                "city":city.name,
                "total_records":paginator.count,
                "total_pages":paginator.num_pages,
                "current_page":page,
                "page_size":limit,
                "history":history
            },
            status=status.HTTP_200_OK
        )
    