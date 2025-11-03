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
    from waveshare_epd import epd2in13_V4
except ImportError:
    # Fallback for development/testing without hardware
    epd2in13_V4 = None

logger = logging.getLogger(__name__)

class DisplayManager:
    def __init__(self):
        """Initialize the display manager"""
        # Use landscape orientation like working Pwnagotchi code (250x122)
        self.width = 250
        self.height = 122
        self.epd = None
        
        # Initialize the e-paper display if available
        if epd2in13_V4:
            try:
                self.epd = epd2in13_V4.EPD()
                
                # Comprehensive SPI verification as per Waveshare documentation
                if self._verify_spi_setup():
                    self.epd.init()
                    logger.info("E-paper display (regular B/W) initialized successfully")
                else:
                    logger.warning("SPI verification failed, running in development mode")
                    self.epd = None
            except Exception as e:
                logger.error(f"Failed to initialize e-paper display: {e}")
                logger.info("Running in development mode - images will be saved as PNG files")
                self.epd = None
        else:
            logger.warning("E-paper display module not available (development mode)")
    
    def _verify_spi_setup(self):
        """Verify SPI setup according to Waveshare documentation"""
        import glob
        
        # Check if SPI devices exist
        spi_devices = glob.glob('/dev/spidev*')
        if not spi_devices:
            logger.error("No SPI devices found. Enable SPI with: sudo raspi-config")
            return False
        
        # Check for expected SPI devices (spidev0.0 and spidev0.1)
        expected_devices = ['/dev/spidev0.0', '/dev/spidev0.1']
        found_devices = [dev for dev in expected_devices if os.path.exists(dev)]
        
        if len(found_devices) < 2:
            logger.warning(f"Expected SPI devices: {expected_devices}")
            logger.warning(f"Found SPI devices: {spi_devices}")
            logger.warning("SPI may be partially configured or occupied by other drivers")
        
        # Check if SPI is enabled in boot config
        try:
            with open('/boot/config.txt', 'r') as f:
                config_content = f.read()
                if 'dtparam=spi=on' not in config_content:
                    logger.warning("SPI not enabled in /boot/config.txt. Run: sudo raspi-config")
                    return False
        except FileNotFoundError:
            logger.warning("Could not verify /boot/config.txt (may not be on Raspberry Pi)")
        except PermissionError:
            logger.warning("Permission denied reading /boot/config.txt")
        
        # At minimum, we need spidev0.0 for the display
        if os.path.exists('/dev/spidev0.0'):
            logger.info(f"SPI verification passed. Available devices: {spi_devices}")
            return True
        else:
            logger.error("Primary SPI device /dev/spidev0.0 not found")
            return False
    
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
        """Create weather display image (black/white only) - Landscape layout for 250x122"""
        # Create image with natural dimensions - official driver handles rotation
        image = Image.new('1', (self.width, self.height), 255)
        draw = ImageDraw.Draw(image)
        
        # Fonts for landscape layout
        font_large = self.get_font(24)
        font_medium = self.get_font(16)
        font_small = self.get_font(12)
        
        # Current time
        current_time = datetime.now().strftime("%H:%M")
        current_date = datetime.now().strftime("%d.%m.%Y")
        
        # Layout for landscape display (250x122)
        margin = 5
        
        # Top row - Date and time
        draw.text((margin, margin), current_date, font=font_small, fill=0)
        time_width = draw.textbbox((0, 0), current_time, font=font_small)[2]
        draw.text((self.width - time_width - margin, margin), current_time, font=font_small, fill=0)
        
        # City name
        city = weather_data.get('city', 'Unknown')
        draw.text((margin, 20), city, font=font_medium, fill=0)
        
        # Temperature (large, prominent)
        temp = weather_data.get('temperature', 0)
        temp_text = f"{temp:.1f}°C"
        draw.text((margin, 45), temp_text, font=font_large, fill=0)
        
        # Weather description
        description = weather_data.get('description', 'Unknown')
        if len(description) > 20:
            description = description[:20] + "..."
        draw.text((margin, 75), description.title(), font=font_medium, fill=0)
        
        # Right side - Additional info
        right_x = 130
        humidity = weather_data.get('humidity', 0)
        pressure = weather_data.get('pressure', 0)
        wind_speed = weather_data.get('wind_speed', 0)
        wind_dir = weather_data.get('wind_direction', 0)
        
        draw.text((right_x, 20), f"Luftfeuchtigkeit:", font=font_small, fill=0)
        draw.text((right_x, 32), f"{humidity}%", font=font_small, fill=0)
        
        draw.text((right_x, 50), f"Luftdruck:", font=font_small, fill=0)
        draw.text((right_x, 62), f"{pressure} hPa", font=font_small, fill=0)
        
        draw.text((right_x, 80), f"Wind: {wind_speed:.1f}m/s", font=font_small, fill=0)
        draw.text((right_x, 92), f"Richtung: {wind_dir}°", font=font_small, fill=0)
        
        # Separator line
        draw.line([(120, 20), (120, 110)], fill=0, width=1)
        
        # Rotate image 180 degrees
        image = image.rotate(180)
        
        return image
    
    def show_weather(self, weather_data):
        """Display weather data on the e-ink screen"""
        try:
            # Create the weather image (black/white only)
            image = self.create_weather_image(weather_data)
            
            if self.epd:
                # Convert image to display buffer format
                buffer = self.epd.getbuffer(image)
                
                # Display on e-paper (single image for B/W display)
                self.epd.display(buffer)
                logger.info("Weather data displayed on e-paper")
            else:
                # Save image for development/testing
                image.save('weather_display.png')
                logger.info("Weather image saved (development mode)")
                
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
