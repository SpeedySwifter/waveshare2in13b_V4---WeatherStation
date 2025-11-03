"""
Weather API Module
Fetches weather data from OpenWeatherMap API
"""

import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WeatherAPI:
    def __init__(self, api_key, city="Berlin"):
        """
        Initialize Weather API client
        
        Args:
            api_key (str): OpenWeatherMap API key
            city (str): City name for weather data
        """
        self.api_key = api_key
        self.city = city
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
    def get_current_weather(self):
        """
        Fetch current weather data
        
        Returns:
            dict: Weather data or None if failed
        """
        try:
            # API endpoint for current weather
            url = f"{self.base_url}/weather"
            params = {
                'q': self.city,
                'appid': self.api_key,
                'units': 'metric',  # Celsius
                'lang': 'de'  # German language
            }
            
            logger.info(f"Fetching weather data for {self.city}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract relevant weather information
            weather_data = {
                'city': data['name'],
                'country': data['sys']['country'],
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'wind_speed': data.get('wind', {}).get('speed', 0),
                'wind_direction': data.get('wind', {}).get('deg', 0),
                'visibility': data.get('visibility', 0) / 1000,  # Convert to km
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"Weather data fetched successfully: {weather_data['temperature']:.1f}°C, {weather_data['description']}")
            return weather_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching weather data: {e}")
            return None
        except KeyError as e:
            logger.error(f"Error parsing weather data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching weather data: {e}")
            return None
    
    def get_forecast(self, days=5):
        """
        Fetch weather forecast
        
        Args:
            days (int): Number of days for forecast (max 5)
            
        Returns:
            list: List of forecast data or None if failed
        """
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': self.city,
                'appid': self.api_key,
                'units': 'metric',
                'lang': 'de'
            }
            
            logger.info(f"Fetching {days}-day forecast for {self.city}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract forecast data (API returns 3-hour intervals)
            forecast_list = []
            for item in data['list'][:days * 8]:  # 8 intervals per day
                forecast_data = {
                    'datetime': item['dt_txt'],
                    'temperature': item['main']['temp'],
                    'description': item['weather'][0]['description'],
                    'humidity': item['main']['humidity'],
                    'wind_speed': item.get('wind', {}).get('speed', 0)
                }
                forecast_list.append(forecast_data)
            
            logger.info(f"Forecast data fetched successfully: {len(forecast_list)} entries")
            return forecast_list
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching forecast data: {e}")
            return None
        except KeyError as e:
            logger.error(f"Error parsing forecast data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching forecast data: {e}")
            return None
