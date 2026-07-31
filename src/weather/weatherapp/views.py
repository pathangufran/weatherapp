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
from django.db.models import Avg,Max,Min,Count,Subquery,OuterRef
from weatherapp.redis_service import RedisService
from weatherapp.repository import WeatherRepository
from common.throttling import WeatherThrottle

logger = logging.getLogger(__name__)

class WeatherCurrent(APIView):

    permission_classes = [IsAuthenticated]
    throttle_classes = [WeatherThrottle]

    def post(self, request):

        city_id = request.data.get("city_id")
        if not UserCity.objects.filter(user=request.user,city_id=city_id).exists():
            return Response(
                {'message':'You are not tracking this city.'},
                status=status.HTTP_403_FORBIDDEN
            )

        city = get_object_or_404(City, id=city_id)

        cached_weather = RedisService.get_current_weather(city_id)
        if cached_weather:
            return Response(
                {
                    "message":"Weather fetched successfully.",
                    "source":"redis",
                    "data":cached_weather
                },
                status=status.HTTP_200_OK
            )

        try:
            data = weather_data(city_id)
            current = data["current"]

            weather = WeatherRepository.create(city,current)

            logger.info("Weather record saved for %s", city.name)
            response_data = {
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

            return Response(
                {
                    "message": "Weather fetched successfully",
                    "source": "weather_api",
                    "data":response_data
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
    throttle_classes = [WeatherThrottle]

    def get(self,request):

        city_id = request.query_params.get('city_id')
        if not UserCity.objects.filter(user=request.user,city_id=city_id).exists():
            return Response(
                {"message": "You are not tracking this city."},
                status=status.HTTP_403_FORBIDDEN,
            )
        city = get_object_or_404(City,id=city_id)

        cached_weather = RedisService.get_latest_weather(city_id)
        if cached_weather:
            return Response(
                {
                    "message": "Latest weather fetched successfully.",
                    "source": "redis",
                    "data": cached_weather
                },
                status=status.HTTP_200_OK
            )

        weather = WeatherRecord.objects.get(city=city)
        if not weather:
            return Response(
                {'message':'No weather record found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        response_data = {
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

        return Response(
            {
                "message": "Weather fetched successfully",
                "source": "weather_api",
                "data":response_data
            },
            status=status.HTTP_200_OK,
        )
    
class WeatherForecast(APIView):

    permission_classes = [IsAuthenticated]
    throttle_classes = [WeatherThrottle]

    def post(self, request):

        city_id = request.data.get("city_id")
        if not UserCity.objects.filter(user=request.user,city_id=city_id).exists():
            return Response(
                {'message':'You are not tracking this city.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        cached_forecast = RedisService.get_weather_forecast(city_id)
        if cached_forecast:
            return Response(
                {
                    "message": "Forecast fetched successfully.",
                    "source": "redis",
                    "data": cached_forecast
                },
                status=status.HTTP_200_OK
            )

        city = get_object_or_404(City, id=city_id)

        try:
            data = forecast_data(city_id)
            logger.info("Weather record saved for %s", city.name)
            RedisService.set_weather_forecast(city_id,data)
            
            return Response(
                {
                    "message": "Weather fetched successfully.",
                    "source": "weather_api",
                    "data": data
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

class WeatherHistory(APIView):

    permission_classes = [IsAuthenticated]
    throttle_classes = [WeatherThrottle]

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
        
        cached_history = RedisService.get_weather_history(
            city_id,
            page,
            limit,
            start_date,
            end_date
        )
        if cached_history:
            logger.info(
                "History served from Redis for %s",
                city.name,
            )
            return Response(
                {
                    "message": "History fetched successfully.",
                    "source": "redis",
                    "data": cached_history
                },
                status=status.HTTP_200_OK
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
        response_data = {
            "city":city.name,
            "total_records":paginator.count,
            "total_pages":paginator.num_pages,
            "current_page":page,
            "page_size":limit,
            "history":history
        }
        RedisService.set_weather_history(
            city_id,
            page,
            limit,
            start_date,
            end_date,
            response_data
        )
        return Response(
            {
                "message": "History fetched successfully.",
                "source": "database",
                "data": response_data
            },
            status=status.HTTP_200_OK
        )
    
class WeatherStatistics(APIView):

    permission_classes = [IsAuthenticated]
    throttle_classes = [WeatherThrottle]

    def get(self,request):

        city_id = request.query_params.get('city_id')
        if not UserCity.objects.filter(user=request.user,city_id=city_id).exists():
            logger.warning(
                "%s tried to access city %s",
                request.user.username,
                city_id
            )

        cached_statistics = RedisService.get_weather_statistics(city_id)
        if cached_statistics:
            return Response(
                {
                    "message": "Statistics fetched successfully.",
                    "source": "redis",
                    "data": cached_statistics
                },
                status=status.HTTP_200_OK
            )

        city = get_object_or_404(City,id=city_id)
        queryset = WeatherRecord.objects.filter(city=city)
        if not queryset:
            return Response(
                {"message": "No weather records found."},
                status=status.HTTP_404_NOT_FOUND
            )
        weather = queryset.aggregate(
            total_records=Count("id"),
            average_temp=Avg("temparature"),
            maximum_temp=Max("temparature"),
            minimum_temp=Min("temparature"),
            average_humidity=Avg("humidity"),
            average_pressure=Avg("pressure"),
            average_wind_speed=Avg("wind_speed"),
        )
        logger.info(
            "Weather statistics fetched for %s",
            city.name
        )
        response_data = {
            "total_records": weather["total_records"],
            "average_temperature": round(weather["average_temp"],2),
            "maximum_temperature": weather["maximum_temp"],
            "minimum_temperature": weather["minimum_temp"],
            "average_humidity": round(weather["average_humidity"],2),
            "average_pressure": round(weather["average_pressure"],2),
            "average_wind_speed": round(weather["average_wind_speed"],2),
            "first_recorded_at": weather.last().recorded_at,
            "latest_recorded_at": weather.first().recorded_at,
        }
        RedisService.set_weather_statistics(city_id,response_data)
        
        return Response(
            {
                "message": "Statistics fetched successfully.",
                "source": "database",
                "data": response_data
            },
            status=status.HTTP_200_OK
        )
    
class WeatherCompare(APIView):

    permission_classes = [IsAuthenticated]
    throttle_classes = [WeatherThrottle]
    
    def get(self,request):

        city_ids = request.query_params.get('cities')
        if not city_ids:
            return Response(
                {"message": "cities query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            city_ids = [int(city.strip()) for city in city_ids.split(",")]

        except ValueError:
            return Response(
                {"message": "Invalid city ids."},
                status=status.HTTP_400_BAD_REQUEST
            ) 
        curr_weather = WeatherRecord.objects.filter(
            city=OuterRef("city")
        ).order_by("-recorded_at")
        queryset = (
            UserCity.objects.filter(
            user=request.user,
            city_id__in=city_ids
            ).select_related("city") \
            .annotate(
                temperature=Subquery(curr_weather.values("temperature")[:1]),
                feels_like=Subquery(curr_weather.values("feels_like")[:1]),
                humidity=Subquery(curr_weather.values("humidity")[:1]),
                pressure=Subquery(curr_weather.values("pressure")[:1]),
                wind_speed=Subquery(curr_weather.values("wind_speed")[:1]),
                visibility=Subquery(curr_weather.values("visibility")[:1]),
                weather=Subquery(curr_weather.values("weather")[:1]),
                weather_code=Subquery(curr_weather.values("weather_code")[:1]),
                icon=Subquery(curr_weather.values("icon")[:1]),
                recorded_at=Subquery(curr_weather.values("recorded_at")[:1]),   
            )
        )   
        if not queryset.exists():
            return Response(
                {"message": "No matching cities found."},
                status=status.HTTP_404_NOT_FOUND
            )

        response = []
        for city in queryset:
            data = {
                "city_id": city.city.id,
                "city": city.city.name,
                "state": city.city.state,
                "country": city.city.country,
                "temperature": city.temperature,
                "feels_like": city.feels_like,
                "humidity": city.humidity,
                "pressure": city.pressure,
                "wind_speed": city.wind_speed,
                "visibility": city.visibility,
                "condition": city.weather,
                "weather_code": city.weather_code,
                "icon": city.icon,
                "recorded_at": city.recorded_at,
            }
            response.append(data)

        logger.info(
            "%s compared %d cities",
            request.user.username,
            len(response)
        )
        return Response(
            {"count": len(response),"cities": response},
            status=status.HTTP_200_OK
        )
        