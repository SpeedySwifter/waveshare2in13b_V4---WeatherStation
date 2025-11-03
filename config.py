"""
Configuration Module for Weather Station
Handles loading and managing configuration settings
"""

import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Config:
    def __init__(self, config_file="config.json"):
        """
        Initialize configuration
        
        Args:
            config_file (str): Path to configuration file
        """
        self.config_file = config_file
        self.config_data = {}
        
        # Default configuration
        self.defaults = {
            "api_key": "",
            "city": "Berlin",
            "country_code": "DE",
            "update_interval": 30,  # minutes
            "display_rotation": 0,
            "language": "de",
            "units": "metric"
        }
        
        self.load_config()
    
    def load_config(self):
        """Load configuration from file or create default"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config_data = json.load(f)
                logger.info(f"Configuration loaded from {self.config_file}")
            else:
                logger.info("Configuration file not found, creating default")
                self.config_data = self.defaults.copy()
                self.save_config()
                
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self.config_data = self.defaults.copy()
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=4, ensure_ascii=False)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
    
    def get(self, key, default=None):
        """Get configuration value"""
        return self.config_data.get(key, default)
    
    def set(self, key, value):
        """Set configuration value"""
        self.config_data[key] = value
        self.save_config()
    
    @property
    def api_key(self):
        """Get OpenWeatherMap API key"""
        api_key = self.config_data.get('api_key', '')
        if not api_key:
            # Try to get from environment variable
            api_key = os.getenv('OPENWEATHER_API_KEY', '')
        return api_key
    
    @property
    def city(self):
        """Get city name"""
        return self.config_data.get('city', 'Berlin')
    
    @property
    def country_code(self):
        """Get country code"""
        return self.config_data.get('country_code', 'DE')
    
    @property
    def update_interval(self):
        """Get update interval in minutes"""
        return self.config_data.get('update_interval', 30)
    
    @property
    def display_rotation(self):
        """Get display rotation"""
        return self.config_data.get('display_rotation', 0)
    
    @property
    def language(self):
        """Get language code"""
        return self.config_data.get('language', 'de')
    
    @property
    def units(self):
        """Get units (metric/imperial)"""
        return self.config_data.get('units', 'metric')
