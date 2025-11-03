"""
Display Manager for Weather Station
Handles the e-ink display rendering and layout
"""

import logging
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os
import sys

# Try to import cairosvg for SVG rendering
try:
    import cairosvg
    SVG_SUPPORT = True
except (ImportError, OSError) as e:
    SVG_SUPPORT = False
    # Only log warning if we're on a Raspberry Pi (where SVG support is expected)
    if 'arm' in os.uname().machine.lower() or os.path.exists('/proc/cpuinfo'):
        logging.warning(f"cairosvg not available - SVG icons will fallback to ASCII art: {e}")
    # On development machines (Mac/Windows), this is expected

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
        
        # Set up icons directory
        self.icons_dir = os.path.join(os.path.dirname(__file__), 'icons')
        self.icon_cache = {}  # Cache for loaded icons
        
        # Set up fonts directory
        self.fonts_dir = os.path.join(os.path.dirname(__file__), 'Merriweather_Sans')
        self.font_cache = {}  # Cache for loaded fonts
        
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
    
    def get_font(self, size=12, weight='regular', italic=False):
        """Get Merriweather Sans font with specified weight and style"""
        cache_key = f"{size}_{weight}_{italic}"
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
        
        # Map weight names to font files
        weight_mapping = {
            'light': 'Light',
            'regular': 'Regular', 
            'medium': 'Medium',
            'semibold': 'SemiBold',
            'bold': 'Bold',
            'extrabold': 'ExtraBold'
        }
        
        # Build font filename
        weight_name = weight_mapping.get(weight.lower(), 'Regular')
        italic_suffix = 'Italic' if italic else ''
        font_filename = f"MerriweatherSans-{weight_name}{italic_suffix}.ttf"
        
        # Try Merriweather Sans fonts first
        merriweather_paths = [
            os.path.join(self.fonts_dir, 'static', font_filename),
            # Variable font fallback
            os.path.join(self.fonts_dir, 'MerriweatherSans-VariableFont_wght.ttf'),
            os.path.join(self.fonts_dir, 'MerriweatherSans-Italic-VariableFont_wght.ttf') if italic else None
        ]
        
        # System font fallbacks
        system_font_paths = [
            # Linux fonts (Raspberry Pi)
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if weight in ['bold', 'semibold', 'extrabold'] else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if weight in ['bold', 'semibold', 'extrabold'] else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            # macOS fonts
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial.ttf",
        ]
        
        # Try all font paths
        all_paths = [p for p in merriweather_paths if p] + system_font_paths
        
        for font_path in all_paths:
            try:
                font = ImageFont.truetype(font_path, size)
                self.font_cache[cache_key] = font
                return font
            except Exception as e:
                continue
        
        # Final fallback to default font
        default_font = ImageFont.load_default()
        self.font_cache[cache_key] = default_font
        return default_font
    
    def get_weather_icon_filename(self, weather_code, is_day=True):
        """Get weather icon filename based on weather code"""
        # Map weather codes to icon filenames
        icon_mapping = {
            # Clear sky
            0: "clear-day.svg" if is_day else "clear-night.svg",
            # Mainly clear
            1: "cloudy-1-day.svg" if is_day else "cloudy-1-night.svg",
            # Partly cloudy
            2: "cloudy-2-day.svg" if is_day else "cloudy-2-night.svg",
            3: "cloudy-3-day.svg" if is_day else "cloudy-3-night.svg",
            # Overcast
            45: "fog-day.svg" if is_day else "fog-night.svg",  # Fog
            48: "fog-day.svg" if is_day else "fog-night.svg",  # Depositing rime fog
            # Drizzle
            51: "rainy-1-day.svg" if is_day else "rainy-1-night.svg",
            53: "rainy-2-day.svg" if is_day else "rainy-2-night.svg",
            55: "rainy-3-day.svg" if is_day else "rainy-3-night.svg",
            # Rain
            61: "rainy-1-day.svg" if is_day else "rainy-1-night.svg",
            63: "rainy-2-day.svg" if is_day else "rainy-2-night.svg",
            65: "rainy-3-day.svg" if is_day else "rainy-3-night.svg",
            # Snow
            71: "snowy-1-day.svg" if is_day else "snowy-1-night.svg",
            73: "snowy-2-day.svg" if is_day else "snowy-2-night.svg",
            75: "snowy-3-day.svg" if is_day else "snowy-3-night.svg",
            # Thunderstorm
            95: "thunderstorms.svg",
            96: "scattered-thunderstorms-day.svg" if is_day else "scattered-thunderstorms-night.svg",
            99: "severe-thunderstorm.svg"
        }
        return icon_mapping.get(weather_code, "cloudy.svg")
    
    def get_weather_icon_fallback(self, weather_code, is_day=True):
        """Get fallback Unicode weather icon symbol"""
        # Fallback weather icons using Unicode symbols
        weather_icons = {
            0: "☀" if is_day else "☾",
            1: "⛅" if is_day else "☾",
            2: "⛅", 3: "☁",
            45: "≋", 48: "≋",
            51: "∴", 53: "∴", 55: "∴",
            61: "☔", 63: "☔", 65: "☔",
            71: "❄", 73: "❅", 75: "❆",
            95: "⚡", 96: "⚡", 99: "⚡"
        }
        return weather_icons.get(weather_code, "⛅")
    
    def load_svg_icon(self, filename, size=(40, 40)):
        """Load and convert SVG icon to PIL Image"""
        if not SVG_SUPPORT:
            return None
            
        cache_key = f"{filename}_{size[0]}x{size[1]}"
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
            
        icon_path = os.path.join(self.icons_dir, filename)
        if not os.path.exists(icon_path):
            logger.warning(f"Icon file not found: {icon_path}")
            return None
            
        try:
            # Convert SVG to PNG in memory
            png_data = cairosvg.svg2png(
                url=icon_path,
                output_width=size[0],
                output_height=size[1]
            )
            
            # Load PNG data into PIL Image
            from io import BytesIO
            icon_image = Image.open(BytesIO(png_data))
            
            # Convert to grayscale and then to 1-bit for e-ink
            icon_image = icon_image.convert('L')  # Grayscale
            
            # Apply threshold to convert to black/white
            threshold = 128
            icon_image = icon_image.point(lambda x: 0 if x < threshold else 255, mode='1')
            
            # Cache the processed image
            self.icon_cache[cache_key] = icon_image
            return icon_image
            
        except Exception as e:
            logger.error(f"Error loading SVG icon {filename}: {e}")
            return None
    
    def draw_weather_icon_art(self, draw, x, y, weather_code, is_day=True, size="small"):
        """Draw custom ASCII art weather icons"""
        font_small = self.get_font(8, weight='regular')
        font_tiny = self.get_font(6, weight='light')
        
        if size == "large":
            # Large ASCII art icons for main weather display
            if weather_code == 0:  # Clear sky
                if is_day:
                    # Sun
                    lines = [
                        "  \\   |   /  ",
                        "   \\  |  /   ",
                        "--- ( ☀ ) ---",
                        "   /  |  \\   ",
                        "  /   |   \\  "
                    ]
                else:
                    # Moon
                    lines = [
                        "     ****     ",
                        "   **    *   ",
                        "  *   ☾   *  ",
                        "   **    *   ",
                        "     ****     "
                    ]
            elif weather_code in [1, 2]:  # Partly cloudy
                lines = [
                    "   ☀  ~~~    ",
                    "     ~~☁~~   ",
                    "   ~~~   ~~  ",
                    "  ~~       ~ ",
                    "             "
                ]
            elif weather_code == 3:  # Overcast
                lines = [
                    "  ~~~☁~~~   ",
                    " ~~     ~~  ",
                    "~~  ☁☁  ~~~ ",
                    " ~~     ~~  ",
                    "  ~~~~~~~   "
                ]
            elif weather_code in [61, 63, 65]:  # Rain
                lines = [
                    "  ~~☁☁~~    ",
                    " ~~     ~~  ",
                    "~~       ~~ ",
                    " | | ☔ | |  ",
                    " | | | | |  "
                ]
            elif weather_code in [71, 73, 75]:  # Snow
                lines = [
                    "  ~~☁☁~~    ",
                    " ~~     ~~  ",
                    "~~   ❄   ~~ ",
                    " ❅ ❄ ❅ ❄   ",
                    "   ❄ ❅ ❄   "
                ]
            elif weather_code in [95, 96, 99]:  # Thunderstorm
                lines = [
                    "  ~~☁☁~~    ",
                    " ~~     ~~  ",
                    "~~   ⚡   ~~ ",
                    " | ⚡ | | |  ",
                    " | | ⚡ | |  "
                ]
            else:
                # Default cloud
                lines = [
                    "   ~~~~~~    ",
                    "  ~~☁☁~~   ",
                    " ~~    ~~  ",
                    "~~      ~~ ",
                    " ~~~~~~~~  "
                ]
            
            # Draw the ASCII art
            for i, line in enumerate(lines):
                draw.text((x, y + i * 8), line, font=font_tiny, fill=0)
        
        else:
            # Small icon for details section
            icon = self.get_weather_icon_fallback(weather_code, is_day)
            draw.text((x, y), icon, font=font_small, fill=0)
    
    def draw_detail_icons(self, draw, x, y, icon_type):
        """Draw custom icons for weather details"""
        font_small = self.get_font(8, weight='regular')
        
        icons = {
            'humidity': {
                'symbol': '💧',
                'ascii': [
                    " ● ",
                    "●●●",
                    " ● "
                ]
            },
            'pressure': {
                'symbol': '📊',
                'ascii': [
                    "█  ",
                    "██ ",
                    "███"
                ]
            },
            'wind': {
                'symbol': '💨',
                'ascii': [
                    "~~~",
                    ">> ",
                    "~~~"
                ]
            },
            'direction': {
                'symbol': '🧭',
                'ascii': [
                    " ↑ ",
                    "←●→",
                    " ↓ "
                ]
            }
        }
        
        if icon_type in icons:
            # Try Unicode symbol first
            try:
                draw.text((x, y), icons[icon_type]['symbol'], font=font_small, fill=0)
                return 15  # Width for Unicode symbol
            except:
                # Fallback to ASCII art
                for i, line in enumerate(icons[icon_type]['ascii']):
                    draw.text((x, y + i * 3), line, font=self.get_font(6, weight='light'), fill=0)
                return 20  # Width for ASCII art
        
        return 10  # Default width
    
    def draw_rounded_rect(self, draw, coords, radius=5, fill=None, outline=None, width=1):
        """Draw a rounded rectangle"""
        x1, y1, x2, y2 = coords
        
        # Draw the main rectangle
        draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill, outline=outline, width=width)
        draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill, outline=outline, width=width)
        
        # Draw the corners
        draw.pieslice([x1, y1, x1 + 2*radius, y1 + 2*radius], 180, 270, fill=fill, outline=outline, width=width)
        draw.pieslice([x2 - 2*radius, y1, x2, y1 + 2*radius], 270, 360, fill=fill, outline=outline, width=width)
        draw.pieslice([x1, y2 - 2*radius, x1 + 2*radius, y2], 90, 180, fill=fill, outline=outline, width=width)
        draw.pieslice([x2 - 2*radius, y2 - 2*radius, x2, y2], 0, 90, fill=fill, outline=outline, width=width)
    
    def create_weather_image(self, weather_data):
        """Create modern weather display image with improved design"""
        # Create image with natural dimensions
        image = Image.new('1', (self.width, self.height), 255)
        draw = ImageDraw.Draw(image)
        
        # Enhanced fonts with Merriweather Sans hierarchy
        font_title = self.get_font(14, weight='semibold')
        font_temp = self.get_font(32, weight='bold')  # Larger for better prominence
        font_medium = self.get_font(12, weight='medium')
        font_small = self.get_font(10, weight='regular')
        font_tiny = self.get_font(8, weight='light')
        
        # Current time and date
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_date = now.strftime("%d.%m.%Y")
        weekday = now.strftime("%A")[:2].upper()  # Short weekday
        
        # Colors (for monochrome: 0=black, 255=white)
        BLACK = 0
        WHITE = 255
        
        # Layout constants
        margin = 4
        header_height = 18
        
        # === HEADER SECTION ===
        # Header background
        draw.rectangle([0, 0, self.width, header_height], fill=BLACK)
        
        # Date and time in header (white text on black background)
        draw.text((margin, 2), f"{weekday} {current_date}", font=font_small, fill=WHITE)
        time_bbox = draw.textbbox((0, 0), current_time, font=font_small)
        time_width = time_bbox[2] - time_bbox[0]
        draw.text((self.width - time_width - margin, 2), current_time, font=font_small, fill=WHITE)
        
        # === MAIN CONTENT AREA ===
        content_y = header_height + 3
        
        # City name with underline
        city = weather_data.get('city', 'Unknown')
        draw.text((margin, content_y), city, font=font_title, fill=BLACK)
        city_bbox = draw.textbbox((margin, content_y), city, font=font_title)
        draw.line([(margin, city_bbox[3] + 1), (city_bbox[2], city_bbox[3] + 1)], fill=BLACK, width=1)
        
        # === LEFT COLUMN - TEMPERATURE AND WEATHER ===
        temp_y = content_y + 20
        
        # Temperature (large and prominent)
        temp = weather_data.get('temperature', 0)
        temp_text = f"{temp:.0f}°"
        draw.text((margin, temp_y), temp_text, font=font_temp, fill=BLACK)
        
        # Weather icon (enhanced with ASCII art)
        weather_code = weather_data.get('weather_code', 0)
        is_day = weather_data.get('is_day', True)
        
        # Position for large weather icon
        temp_bbox = draw.textbbox((margin, temp_y), temp_text, font=font_temp)
        icon_x = temp_bbox[2] + 8
        
        # Draw weather icon (SVG or fallback)
        try:
            # Try to load SVG icon first
            icon_filename = self.get_weather_icon_filename(weather_code, is_day)
            icon_image = self.load_svg_icon(icon_filename, size=(50, 40))
            
            if icon_image:
                # Paste the SVG icon
                image.paste(icon_image, (icon_x, temp_y - 5))
            else:
                # Fallback to ASCII art
                self.draw_weather_icon_art(draw, icon_x, temp_y - 5, weather_code, is_day, "large")
        
        except Exception as e:
            logger.warning(f"Error drawing weather icon: {e}")
            # Final fallback to simple Unicode icon
            weather_icon = self.get_weather_icon_fallback(weather_code, is_day)
            try:
                icon_font = self.get_font(16, weight='medium')
                draw.text((icon_x, temp_y + 5), weather_icon, font=icon_font, fill=BLACK)
            except:
                pass
        
        # Weather description
        description = weather_data.get('description', 'Unknown')
        if len(description) > 18:
            description = description[:18] + "..."
        desc_y = temp_y + 35
        draw.text((margin, desc_y), description.title(), font=font_medium, fill=BLACK)
        
        # === RIGHT COLUMN - DETAILS ===
        right_x = 140
        detail_y = content_y + 20
        
        # Decorative border for details section
        detail_box = [right_x - 3, detail_y - 2, self.width - margin, self.height - margin]
        draw.rectangle(detail_box, outline=BLACK, width=1)
        
        # Details with icons/symbols
        humidity = weather_data.get('humidity', 0)
        pressure = weather_data.get('pressure', 0)
        wind_speed = weather_data.get('wind_speed', 0)
        wind_dir = weather_data.get('wind_direction', 0)
        
        details = [
            ('humidity', f"{humidity}%", "Luftf."),
            ('pressure', f"{pressure:.0f}", "hPa"),
            ('wind', f"{wind_speed:.1f}", "m/s"),
            ('direction', f"{wind_dir}°", "")
        ]
        
        for i, (icon_type, value, unit) in enumerate(details):
            y_pos = detail_y + (i * 16)
            
            # Draw custom icon
            icon_width = self.draw_detail_icons(draw, right_x, y_pos, icon_type)
            text_x = right_x + icon_width
            
            # Value and unit
            draw.text((text_x, y_pos), value, font=font_small, fill=BLACK)
            if unit:
                value_bbox = draw.textbbox((text_x, y_pos), value, font=font_small)
                draw.text((value_bbox[2] + 2, y_pos), unit, font=font_tiny, fill=BLACK)
        
        # === DECORATIVE ELEMENTS ===
        # Bottom border line
        draw.line([(margin, self.height - 3), (self.width - margin, self.height - 3)], fill=BLACK, width=1)
        
        # Corner decorations
        corner_size = 3
        # Top left corner
        draw.line([(0, header_height + corner_size), (0, header_height), (corner_size, header_height)], fill=BLACK, width=1)
        # Top right corner  
        draw.line([(self.width - corner_size, header_height), (self.width, header_height), (self.width, header_height + corner_size)], fill=BLACK, width=1)
        
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
