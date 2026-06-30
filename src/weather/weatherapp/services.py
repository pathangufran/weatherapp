import requests
import os
from dotenv import load_dotenv
from django.shortcuts import get_object_or_404
from cities.models import *

load_dotenv()

API_KEY = os.getenv("API_KEY")

class WeatherServiceError(Exception):
    """Raised when weather data cannot be fetched."""
    pass

def weather_data(city_id):

    WEATHER_API_URL = "http://api.weatherapi.com/v1/current.json"
    try:
        city = get_object_or_404(City, id=city_id)
        response = requests.get(
            WEATHER_API_URL,
            params={"key": API_KEY,"q": city.name,},
            timeout=10,
        )

        response.raise_for_status()

    except requests.RequestException as exc:
        raise WeatherServiceError("Unable to fetch weather data.") from exc
    
    return response.json()