"""
Enhanced Display Manager for Weather Station
Features:
- Weather Icons font integration
- Day/Night mode support
- Improved layout with current weather and 2-day forecast
- Better typography and visual hierarchy
"""

import os
import logging
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import time

# Add the waveshare_epd directory to the path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'waveshare_epd'))

try:
    from waveshare_epd import epd2in13_V4
    EPD_AVAILABLE = True
except ImportError:
    EPD_AVAILABLE = False
    print("Running in simulation mode - hardware display not available")

logger = logging.getLogger(__name__)

# Weather Icons mapping (using Weather Icons 2.0)
WEATHER_ICONS = {
    # Day icons
    'clear-day': '\uf00d',
    'partly-cloudy-day': '\uf002',
    'cloudy': '\uf013',
    'fog': '\uf014',
    'rain': '\uf019',
    'snow': '\uf01b',
    'thunderstorm': '\uf01e',
    'wind': '\uf050',
    'hail': '\uf015',
    'tornado': '\uf056',
    # Night icons
    'clear-night': '\uf02e',
    'partly-cloudy-night': '\uf031',
    # Default
    'default': '\uf03e'
}

class EnhancedDisplayManager:
    def __init__(self):
        """Initialize the enhanced display manager"""
        # Display dimensions (landscape mode)
        self.width = 250
        self.height = 122
        
        # Initialize display if available
        self.epd = None
        if EPD_AVAILABLE:
            try:
                self.epd = epd2in13_V4.EPD()
                self.epd.init()
                self.epd.Clear(0xFF)
            except Exception as e:
                logger.error(f"Failed to initialize display: {e}")
                self.epd = None
        
        # Load fonts
        self._load_fonts()
        
        # Create image buffers
        self.image_black = Image.new('1', (self.width, self.height), 255)  # 1 for black/white
        self.image_red = Image.new('1', (self.width, self.height), 255)    # 1 for red
        
        # Drawing contexts
        self.draw_black = ImageDraw.Draw(self.image_black)
        self.draw_red = ImageDraw.Draw(self.image_red)
    
    def _load_fonts(self):
        """Load required fonts with fallbacks"""
        try:
            # Try to load Lato font (downloaded by download_weather_icons.sh)
            self.font_small = ImageFont.truetype('fonts/Lato-Regular.ttf', 12)
            self.font_medium = ImageFont.truetype('fonts/Lato-Bold.ttf', 16)
            self.font_large = ImageFont.truetype('fonts/Lato-Bold.ttf', 24)
            self.font_icons = ImageFont.truetype('fonts/weathericons-regular-webfont.ttf', 24)
        except Exception as e:
            logger.warning(f"Could not load custom fonts: {e}")
            # Fall back to default fonts
            self.font_small = ImageFont.load_default()
            self.font_medium = ImageFont.load_default()
            self.font_large = ImageFont.load_default()
            self.font_icons = ImageFont.load_default()
    
    def _draw_weather_icon(self, x, y, condition, is_day=True, size=24):
        """Draw a weather icon at the specified position"""
        icon_key = condition.lower()
        if not is_day and icon_key.endswith('-day'):
            icon_key = icon_key.replace('-day', '-night')
        
        icon_char = WEATHER_ICONS.get(icon_key, WEATHER_ICONS['default'])
        self.draw_black.text((x, y), icon_char, font=self.font_icons, fill=0)
        
        # Return the icon dimensions
        return self.font_icons.getsize(icon_char)
    
    def _draw_centered_text(self, text, y, font, color='black'):
        """Draw centered text at the specified y position"""
        draw = self.draw_black if color == 'black' else self.draw_red
        text_width = draw.textlength(text, font=font)
        x = (self.width - text_width) // 2
        draw.text((x, y), text, font=font, fill=0)
        return y + font.size + 2
    
    def update_display(self, weather_data):
        """Update the display with new weather data"""
        if not weather_data:
            logger.error("No weather data provided")
            return
        
        # Clear the display buffers
        self.draw_black.rectangle((0, 0, self.width, self.height), fill=255)
        self.draw_red.rectangle((0, 0, self.width, self.height), fill=255)
        
        # Get current time for day/night determination
        current_hour = datetime.now().hour
        is_day = 6 <= current_hour < 18  # Simple day/night detection
        
        # Draw header with location and date
        try:
            location = weather_data.get('location', 'Unknown')
            self._draw_centered_text(location, 2, self.font_medium)
            
            date_str = datetime.now().strftime('%a, %b %d')
            self._draw_centered_text(date_str, 20, self.font_small)
            
            # Draw current weather (large icon and temperature)
            current_temp = f"{weather_data.get('current_temp', '--')}°C"
            current_condition = weather_data.get('current_condition', 'clear-day')
            
            # Draw current weather icon
            icon_x = (self.width - 60) // 2
            self._draw_weather_icon(icon_x, 40, current_condition, is_day, 40)
            
            # Draw current temperature
            temp_width = self.font_large.getlength(current_temp)
            temp_x = (self.width - temp_width) // 2
            self.draw_black.text((temp_x, 40), current_temp, font=self.font_large, fill=0)
            
            # Draw forecast for next 2 days
            forecast = weather_data.get('forecast', [])
            if len(forecast) >= 2:
                # Day 1 forecast
                day1 = forecast[0]
                day1_icon_x = 30
                self._draw_weather_icon(day1_icon_x, 80, day1.get('condition', 'clear-day'), is_day, 20)
                self.draw_black.text((day1_icon_x + 30, 85), f"{day1.get('high', '--')}°", font=self.font_medium, fill=0)
                self.draw_black.text((day1_icon_x + 30, 100), f"{day1.get('low', '--')}°", font=self.font_small, fill=0)
                
                # Day 2 forecast
                day2 = forecast[1]
                day2_icon_x = 150
                self._draw_weather_icon(day2_icon_x, 80, day2.get('condition', 'clear-day'), is_day, 20)
                self.draw_black.text((day2_icon_x + 30, 85), f"{day2.get('high', '--')}°", font=self.font_medium, fill=0)
                self.draw_black.text((day2_icon_x + 30, 100), f"{day2.get('low', '--')}°", font=self.font_small, fill=0)
            
            # Add a subtle border
            self.draw_black.rectangle([0, 0, self.width-1, self.height-1], outline=0)
            
            # Update the display
            if self.epd:
                self.epd.display(self.epd.getbuffer(self.image_black), self.epd.getbuffer(self.image_red))
            
            # Save a preview image for debugging
            self.image_black.save('weather_display_preview.png')
            
        except Exception as e:
            logger.error(f"Error updating display: {e}")
    
    def clear(self):
        """Clear the display"""
        if self.epd:
            self.epd.Clear(0xFF)
            self.epd.sleep()

# Example usage
if __name__ == "__main__":
    # Test data
    test_data = {
        'location': 'Berlin, DE',
        'current_temp': 22,
        'current_condition': 'partly-cloudy-day',
        'forecast': [
            {'day': 'Mon', 'high': 24, 'low': 16, 'condition': 'partly-cloudy-day'},
            {'day': 'Tue', 'high': 26, 'low': 18, 'condition': 'clear-day'}
        ]
    }
    
    # Initialize and test the display
    display = EnhancedDisplayManager()
    try:
        display.update_display(test_data)
        print("Display updated with test data. Check weather_display_preview.png")
    finally:
        # Make sure to clear the display when done
        display.clear()
