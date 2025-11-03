#!/usr/bin/env python3
"""
Weather Station for Raspberry Pi Zero 2 with Waveshare 2.13" V4 E-ink Display
Displays current weather data fetched from Open-Meteo API
"""

import time
import logging
from datetime import datetime
from weather_api import WeatherAPI
from display_manager import DisplayManager
from config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weather_station.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WeatherStation:
    def __init__(self):
        """Initialize the weather station"""
        self.config = Config()
        self.weather_api = WeatherAPI(self.config.latitude, self.config.longitude)
        self.display = DisplayManager()
        logger.info("Weather Station initialized")
    
    def update_display(self):
        """Fetch weather data and update the display"""
        try:
            # Fetch current weather data
            weather_data = self.weather_api.get_weather_data()
            if weather_data:
                # Update the display with new data
                self.display.show_weather(weather_data)
                logger.info(f"Display updated successfully at {datetime.now()}")
                return True
            else:
                logger.error("Failed to fetch weather data")
                return False
        except Exception as e:
            logger.error(f"Error updating display: {e}")
            return False
    
    def run(self):
        """Main loop for the weather station"""
        logger.info("Starting weather station main loop")
        
        # Initial display update
        self.update_display()
        
        while True:
            try:
                # Wait for the specified update interval
                time.sleep(self.config.update_interval * 60)  # Convert minutes to seconds
                
                # Update the display
                self.update_display()
                
            except KeyboardInterrupt:
                logger.info("Weather station stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    try:
        station = WeatherStation()
        station.run()
    except Exception as e:
        logger.error(f"Failed to start weather station: {e}")
