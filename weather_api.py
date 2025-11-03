#!/usr/bin/env python3
"""
Weather API Module for Weather Station
Handles fetching weather data from Open-Meteo API
"""

import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WeatherAPI:
    def __init__(self, latitude=54.3233, longitude=13.0814):
        """
        Initialize Weather API
        Default coordinates are for Stralsund, Germany
        """
        self.latitude = latitude
        self.longitude = longitude
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        
    def get_weather_data(self):
        """
        Fetch current weather data from Open-Meteo API
        Returns dictionary with weather information
        """
        try:
            # API parameters for current weather
            params = {
                'latitude': self.latitude,
                'longitude': self.longitude,
                'current': [
                    'temperature_2m',
                    'relative_humidity_2m',
                    'apparent_temperature',
                    'is_day',
                    'precipitation',
                    'weather_code',
                    'surface_pressure',
                    'wind_speed_10m',
                    'wind_direction_10m'
                ],
                'timezone': 'Europe/Berlin',
                'forecast_days': 1
            }
            
            logger.info(f"Fetching weather data for coordinates: {self.latitude}, {self.longitude}")
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            current = data.get('current', {})
            
            # Extract weather information
            weather_data = {
                'city': 'Stralsund',  # Default city name
                'country': 'DE',
                'temperature': current.get('temperature_2m', 0),
                'feels_like': current.get('apparent_temperature', 0),
                'humidity': current.get('relative_humidity_2m', 0),
                'pressure': current.get('surface_pressure', 0),
                'wind_speed': current.get('wind_speed_10m', 0),
                'wind_direction': current.get('wind_direction_10m', 0),
                'weather_code': current.get('weather_code', 0),
                'is_day': current.get('is_day', 1) == 1,
                'description': self._get_weather_description(current.get('weather_code', 0)),
                'visibility': 10.0,  # Default visibility
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Weather data retrieved successfully: {weather_data['temperature']:.1f}°C, {weather_data['description']}")
            return weather_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching weather data: {e}")
            return self._get_fallback_data()
        except Exception as e:
            logger.error(f"Unexpected error in weather API: {e}")
            return self._get_fallback_data()
    
    def _get_weather_description(self, weather_code):
        """
        Convert weather code to German description
        Based on WMO Weather interpretation codes
        """
        descriptions = {
            0: "Klarer Himmel",
            1: "Überwiegend klar",
            2: "Teilweise bewölkt",
            3: "Bedeckt",
            45: "Nebel",
            48: "Nebel mit Reifablagerung",
            51: "Leichter Sprühregen",
            53: "Mäßiger Sprühregen",
            55: "Dichter Sprühregen",
            56: "Leichter gefrierender Sprühregen",
            57: "Dichter gefrierender Sprühregen",
            61: "Leichter Regen",
            63: "Mäßiger Regen",
            65: "Starker Regen",
            66: "Leichter gefrierender Regen",
            67: "Starker gefrierender Regen",
            71: "Leichter Schneefall",
            73: "Mäßiger Schneefall",
            75: "Starker Schneefall",
            77: "Schneekörner",
            80: "Leichte Regenschauer",
            81: "Mäßige Regenschauer",
            82: "Starke Regenschauer",
            85: "Leichte Schneeschauer",
            86: "Starke Schneeschauer",
            95: "Gewitter",
            96: "Gewitter mit leichtem Hagel",
            99: "Gewitter mit starkem Hagel"
        }
        return descriptions.get(weather_code, "Unbekannt")
    
    def _get_fallback_data(self):
        """
        Return fallback weather data when API is unavailable
        """
        logger.warning("Using fallback weather data")
        return {
            'city': 'Stralsund',
            'country': 'DE',
            'temperature': 20.0,
            'feels_like': 19.0,
            'humidity': 65,
            'pressure': 1013.25,
            'wind_speed': 5.0,
            'wind_direction': 180,
            'weather_code': 1,
            'is_day': True,
            'description': 'Überwiegend klar',
            'visibility': 10.0,
            'timestamp': datetime.now().isoformat()
        }
    
    def set_location(self, latitude, longitude, city_name=None):
        """
        Update the location for weather data
        """
        self.latitude = latitude
        self.longitude = longitude
        if city_name:
            self.city_name = city_name
        logger.info(f"Location updated to: {latitude}, {longitude}")

# Example usage
if __name__ == "__main__":
    # Test the weather API
    api = WeatherAPI()
    weather = api.get_weather_data()
    
    print("Weather Data:")
    print(f"  City: {weather['city']}")
    print(f"  Temperature: {weather['temperature']:.1f}°C")
    print(f"  Feels like: {weather['feels_like']:.1f}°C")
    print(f"  Humidity: {weather['humidity']}%")
    print(f"  Pressure: {weather['pressure']:.1f} hPa")
    print(f"  Wind: {weather['wind_speed']:.1f} m/s @ {weather['wind_direction']}°")
    print(f"  Description: {weather['description']}")
    print(f"  Weather Code: {weather['weather_code']}")
    print(f"  Is Day: {weather['is_day']}")
