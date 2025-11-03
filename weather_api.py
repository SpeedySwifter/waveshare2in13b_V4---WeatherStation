"""
Weather API Module
Fetches weather data from Open-Meteo API
"""

import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WeatherAPI:
    def __init__(self, latitude=54.3091, longitude=13.0818, city="Stralsund"):
        """
        Initialize Weather API client
        
        Args:
            latitude (float): Latitude coordinate
            longitude (float): Longitude coordinate
            city (str): City name for display purposes
        """
        self.latitude = latitude
        self.longitude = longitude
        self.city = city
        self.base_url = "https://api.open-meteo.com/v1"
        
    def get_current_weather(self):
        """
        Fetch current weather data
        
        Returns:
            dict: Weather data or None if failed
        """
        try:
            # API endpoint for current weather
            url = f"{self.base_url}/forecast"
            params = {
                'latitude': self.latitude,
                'longitude': self.longitude,
                'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,surface_pressure,wind_speed_10m,wind_direction_10m,is_day',
                'timezone': 'Europe/Berlin',
                'forecast_days': 1
            }
            
            logger.info(f"Fetching weather data for {self.city} ({self.latitude}, {self.longitude})")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            current = data['current']
            
            # Map weather codes to German descriptions (WMO Weather interpretation codes)
            weather_descriptions = {
                0: "Klarer Himmel", 1: "Überwiegend klar", 2: "Teilweise bewölkt", 3: "Bedeckt",
                45: "Nebel", 48: "Nebel mit Reifablagerung",
                51: "Leichter Nieselregen", 53: "Mäßiger Nieselregen", 55: "Starker Nieselregen",
                56: "Leichter gefrierender Nieselregen", 57: "Starker gefrierender Nieselregen",
                61: "Leichter Regen", 63: "Mäßiger Regen", 65: "Starker Regen",
                66: "Leichter gefrierender Regen", 67: "Starker gefrierender Regen",
                71: "Leichter Schneefall", 73: "Mäßiger Schneefall", 75: "Starker Schneefall",
                77: "Schneekörner", 80: "Leichte Regenschauer", 81: "Mäßige Regenschauer",
                82: "Starke Regenschauer", 85: "Leichte Schneeschauer", 86: "Starke Schneeschauer",
                95: "Gewitter", 96: "Gewitter mit leichtem Hagel", 99: "Gewitter mit starkem Hagel"
            }
            
            weather_code = current.get('weather_code', 0)
            description = weather_descriptions.get(weather_code, "Unbekannt")
            
            # Extract relevant weather information
            weather_data = {
                'city': self.city,
                'country': 'DE',
                'temperature': current['temperature_2m'],
                'feels_like': current['apparent_temperature'],
                'humidity': current['relative_humidity_2m'],
                'pressure': current['surface_pressure'],
                'description': description,
                'weather_code': weather_code,
                'is_day': current.get('is_day', 1) == 1,  # Convert to boolean
                'icon': self._get_weather_icon(weather_code),
                'wind_speed': current['wind_speed_10m'],
                'wind_direction': current['wind_direction_10m'],
                'visibility': 10.0,  # Open-Meteo doesn't provide visibility, use default
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
    
    def _get_weather_icon(self, weather_code):
        """
        Map weather code to icon identifier
        
        Args:
            weather_code (int): WMO weather code
            
        Returns:
            str: Icon identifier
        """
        # Map weather codes to simple icon identifiers
        if weather_code == 0:
            return "01d"  # Clear sky
        elif weather_code in [1, 2]:
            return "02d"  # Few clouds
        elif weather_code == 3:
            return "03d"  # Scattered clouds
        elif weather_code in [45, 48]:
            return "50d"  # Mist
        elif weather_code in [51, 53, 55, 56, 57]:
            return "09d"  # Drizzle
        elif weather_code in [61, 63, 65, 66, 67]:
            return "10d"  # Rain
        elif weather_code in [71, 73, 75, 77, 85, 86]:
            return "13d"  # Snow
        elif weather_code in [80, 81, 82]:
            return "09d"  # Shower rain
        elif weather_code in [95, 96, 99]:
            return "11d"  # Thunderstorm
        else:
            return "01d"  # Default
    
    def get_forecast(self, days=5):
        """
        Fetch weather forecast
        
        Args:
            days (int): Number of days for forecast (max 7)
            
        Returns:
            list: List of forecast data or None if failed
        """
        try:
            url = f"{self.base_url}/forecast"
            params = {
                'latitude': self.latitude,
                'longitude': self.longitude,
                'hourly': 'temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code',
                'timezone': 'Europe/Berlin',
                'forecast_days': min(days, 7)  # Open-Meteo supports up to 7 days
            }
            
            logger.info(f"Fetching {days}-day forecast for {self.city}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            hourly = data['hourly']
            
            # Weather code descriptions
            weather_descriptions = {
                0: "Klarer Himmel", 1: "Überwiegend klar", 2: "Teilweise bewölkt", 3: "Bedeckt",
                45: "Nebel", 48: "Nebel mit Reifablagerung",
                51: "Leichter Nieselregen", 53: "Mäßiger Nieselregen", 55: "Starker Nieselregen",
                61: "Leichter Regen", 63: "Mäßiger Regen", 65: "Starker Regen",
                71: "Leichter Schneefall", 73: "Mäßiger Schneefall", 75: "Starker Schneefall",
                80: "Leichte Regenschauer", 81: "Mäßige Regenschauer", 82: "Starke Regenschauer",
                95: "Gewitter", 96: "Gewitter mit leichtem Hagel", 99: "Gewitter mit starkem Hagel"
            }
            
            # Extract forecast data (take every 3rd hour to match 3-hour intervals)
            forecast_list = []
            for i in range(0, len(hourly['time']), 3):
                if len(forecast_list) >= days * 8:  # Limit to requested days
                    break
                    
                weather_code = hourly['weather_code'][i]
                description = weather_descriptions.get(weather_code, "Unbekannt")
                
                forecast_data = {
                    'datetime': hourly['time'][i],
                    'temperature': hourly['temperature_2m'][i],
                    'description': description,
                    'humidity': hourly['relative_humidity_2m'][i],
                    'wind_speed': hourly['wind_speed_10m'][i]
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
