"""
Display Manager for Weather Station
Handles the e-ink display rendering and layout
"""

import logging
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os
import sys

# Add the waveshare_epd directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'waveshare_epd'))

try:
    from waveshare_epd import epd2in13b_V4
except ImportError:
    # Fallback for development/testing without hardware
    epd2in13b_V4 = None

logger = logging.getLogger(__name__)

class DisplayManager:
    def __init__(self):
        """Initialize the display manager"""
        self.width = 250
        self.height = 122
        self.epd = None
        
        # Initialize the e-paper display if available
        if epd2in13b_V4:
            try:
                self.epd = epd2in13b_V4.EPD()
                self.epd.init()
                logger.info("E-paper display initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize e-paper display: {e}")
                self.epd = None
        else:
            logger.warning("E-paper display module not available (development mode)")
    
    def get_font(self, size=12):
        """Get font for text rendering"""
        try:
            # Try to load a system font
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
        except:
            try:
                return ImageFont.truetype("/System/Library/Fonts/Arial.ttf", size)
            except:
                # Fallback to default font
                return ImageFont.load_default()
    
    def create_weather_image(self, weather_data):
        """Create weather display image"""
        # Create images for black and red layers
        image_black = Image.new('1', (self.width, self.height), 255)
        image_red = Image.new('1', (self.width, self.height), 255)
        
        draw_black = ImageDraw.Draw(image_black)
        draw_red = ImageDraw.Draw(image_red)
        
        # Fonts
        font_large = self.get_font(24)
        font_medium = self.get_font(16)
        font_small = self.get_font(12)
        
        # Current time
        current_time = datetime.now().strftime("%H:%M")
        current_date = datetime.now().strftime("%d.%m.%Y")
        
        # Layout positions
        y_pos = 5
        
        # Date and time (black)
        draw_black.text((5, y_pos), current_date, font=font_small, fill=0)
        draw_black.text((self.width - 60, y_pos), current_time, font=font_small, fill=0)
        y_pos += 20
        
        # City name (black)
        city = weather_data.get('city', 'Unknown')
        draw_black.text((5, y_pos), city, font=font_medium, fill=0)
        y_pos += 25
        
        # Temperature (red - main attraction)
        temp = weather_data.get('temperature', 0)
        temp_text = f"{temp:.1f}°C"
        draw_red.text((5, y_pos), temp_text, font=font_large, fill=0)
        y_pos += 30
        
        # Weather description (black)
        description = weather_data.get('description', 'Unknown')
        draw_black.text((5, y_pos), description.title(), font=font_medium, fill=0)
        y_pos += 20
        
        # Additional info (black)
        humidity = weather_data.get('humidity', 0)
        pressure = weather_data.get('pressure', 0)
        
        draw_black.text((5, y_pos), f"Luftfeuchtigkeit: {humidity}%", font=font_small, fill=0)
        y_pos += 15
        draw_black.text((5, y_pos), f"Luftdruck: {pressure} hPa", font=font_small, fill=0)
        
        # Wind info (right side)
        wind_speed = weather_data.get('wind_speed', 0)
        wind_dir = weather_data.get('wind_direction', 0)
        draw_black.text((130, 45), f"Wind:", font=font_small, fill=0)
        draw_black.text((130, 60), f"{wind_speed:.1f} m/s", font=font_small, fill=0)
        draw_black.text((130, 75), f"{wind_dir}°", font=font_small, fill=0)
        
        return image_black, image_red
    
    def show_weather(self, weather_data):
        """Display weather data on the e-ink screen"""
        try:
            # Create the weather images
            image_black, image_red = self.create_weather_image(weather_data)
            
            if self.epd:
                # Convert images to display buffer format
                buffer_black = self.epd.getbuffer(image_black)
                buffer_red = self.epd.getbuffer(image_red)
                
                # Display on e-paper
                self.epd.display(buffer_black, buffer_red)
                logger.info("Weather data displayed on e-paper")
            else:
                # Save images for development/testing
                image_black.save('weather_display_black.png')
                image_red.save('weather_display_red.png')
                logger.info("Weather images saved (development mode)")
                
        except Exception as e:
            logger.error(f"Error displaying weather data: {e}")
    
    def clear_display(self):
        """Clear the e-ink display"""
        if self.epd:
            try:
                self.epd.Clear()
                logger.info("Display cleared")
            except Exception as e:
                logger.error(f"Error clearing display: {e}")
    
    def sleep(self):
        """Put the display to sleep mode"""
        if self.epd:
            try:
                self.epd.sleep()
                logger.info("Display put to sleep")
            except Exception as e:
                logger.error(f"Error putting display to sleep: {e}")
