"""
Display Manager for Weather Station
Handles the e-ink display rendering and layout
"""

import logging
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os
import sys

# PNG icons are used - no Cairo/SVG dependencies needed!

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
        
        # Set up icons directory (Visual Crossing Weather Icons - 3rd Set)
        base_dir = os.path.dirname(__file__)
        candidate_icon_dirs = [
            os.path.join(base_dir, 'visual_crossing_icons'),
            os.path.join(base_dir, '3rd Set - Monochrome')
        ]

        self.icons_dir = None
        for icon_dir in candidate_icon_dirs:
            if os.path.isdir(icon_dir):
                self.icons_dir = icon_dir
                break

        if not self.icons_dir:
            # Default to the first directory and warn when icons are missing
            self.icons_dir = candidate_icon_dirs[0]
            logger.warning(
                "No weather icon directory found. Expected one of: %s", candidate_icon_dirs
            )

        self.icon_cache = {}  # Cache for loaded icons
        
        # Set up fonts directory (Lato fonts)
        self.fonts_dir = os.path.join(os.path.dirname(__file__), 'Lato')
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
        """Get Lato font with specified weight and style"""
        cache_key = f"{size}_{weight}_{italic}"
        if cache_key in self.font_cache:
            return self.font_cache[cache_key]
        
        # Map weight names to font files (Lato naming convention)
        weight_mapping = {
            'light': 'Light',
            'regular': 'Regular', 
            'medium': 'Regular',  # Lato doesn't have Medium, use Regular
            'semibold': 'Bold',   # Lato doesn't have SemiBold, use Bold
            'bold': 'Bold',
            'extrabold': 'Black'  # Lato uses Black for extra bold
        }
        
        # Build font filename (Lato naming convention)
        weight_name = weight_mapping.get(weight.lower(), 'Regular')
        italic_suffix = 'Italic' if italic else ''
        font_filename = f"Lato-{weight_name}{italic_suffix}.ttf"
        
        # Try Lato fonts first
        lato_paths = [
            os.path.join(self.fonts_dir, font_filename),
            # Alternative paths for Lato
            os.path.join(self.fonts_dir, 'static', font_filename),
            os.path.join(self.fonts_dir, f'Lato-Regular.ttf')  # Fallback to Regular
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
        all_paths = [p for p in lato_paths if p] + system_font_paths
        
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
        """Get weather icon filename based on weather code (Visual Crossing 3rd Set)"""
        # Map weather codes to Visual Crossing Weather Icons 3rd Set filenames
        icon_mapping = {
            0: ("clear-day.png", "clear-night.png"),
            1: ("partly-cloudy-day.png", "partly-cloudy-night.png"),
            2: ("partly-cloudy-day.png", "partly-cloudy-night.png"),
            3: ("cloudy.png", "cloudy.png"),
            45: ("fog.png", "fog.png"),
            48: ("fog.png", "fog.png"),
            51: ("showers-day.png", "showers-night.png"),
            53: ("showers-day.png", "showers-night.png"),
            55: ("showers-day.png", "showers-night.png"),
            56: ("sleet.png", "sleet.png"),
            57: ("sleet.png", "sleet.png"),
            61: ("rain.png", "rain.png"),
            63: ("rain.png", "rain.png"),
            65: ("rain.png", "rain.png"),
            66: ("rain-snow.png", "rain-snow.png"),
            67: ("rain-snow.png", "rain-snow.png"),
            68: ("rain-snow.png", "rain-snow.png"),
            69: ("rain-snow.png", "rain-snow.png"),
            71: ("snow.png", "snow.png"),
            73: ("snow.png", "snow.png"),
            75: ("snow.png", "snow.png"),
            77: ("snow.png", "snow.png"),
            80: ("showers-day.png", "showers-night.png"),
            81: ("showers-day.png", "showers-night.png"),
            82: ("showers-day.png", "showers-night.png"),
            85: ("snow-showers-day.png", "snow-showers-night.png"),
            86: ("snow-showers-day.png", "snow-showers-night.png"),
            95: ("thunder-showers-day.png", "thunder-showers-night.png"),
            96: ("hail.png", "hail.png"),
            99: ("hail.png", "hail.png"),
        }

        day_icon, night_icon = icon_mapping.get(weather_code, ("cloudy.png", "cloudy.png"))
        return day_icon if is_day else night_icon
    
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
    
    def load_png_icon(self, filename, size=(40, 40)):
        """Load and process PNG icon for e-ink display"""
        cache_key = f"{filename}_{size[0]}x{size[1]}"
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
            
        icon_path = os.path.join(self.icons_dir, filename)
        if not os.path.exists(icon_path):
            logger.warning(f"Icon file not found: {icon_path}")
            return None
            
        try:
            # Load PNG image
            icon_image = Image.open(icon_path)
            
            # Resize if needed
            if icon_image.size != size:
                icon_image = icon_image.resize(size, Image.Resampling.LANCZOS)
            
            # Convert to grayscale and then to 1-bit for e-ink
            icon_image = icon_image.convert('L')  # Grayscale
            
            # Apply threshold to convert to black/white
            # For Visual Crossing icons (black symbols on white background)
            threshold = 128
            icon_image = icon_image.point(lambda x: 0 if x < threshold else 255, mode='1')  # Keep black symbols
            
            # Cache the processed image
            self.icon_cache[cache_key] = icon_image
            return icon_image
            
        except Exception as e:
            logger.error(f"Error loading PNG icon {filename}: {e}")
            return None
    
    def draw_weather_icon_art(self, draw, x, y, weather_code, is_day=True, size="small"):
        """Draw custom ASCII art weather icons"""
        font_small = self.get_font(10, weight='regular')  # 12 → 10 (-2)
        font_tiny = self.get_font(8, weight='light')      # 10 → 8 (-2)
        
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
        """Draw custom icons for weather details - no icons, text only"""
        # No icons drawn - just return minimal width for text spacing
        return 0  # No width needed since no icons are drawn
    
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
        
        # Enhanced fonts with Lato hierarchy - SMALLER SIZES
        font_title = self.get_font(16, weight='semibold')    # 18 → 16 (-2)
        font_temp = self.get_font(34, weight='bold')         # 38 → 34 (-4) 
        font_medium = self.get_font(14, weight='medium')     # 16 → 14 (-2)
        font_small = self.get_font(12, weight='regular')     # 14 → 12 (-2)
        font_tiny = self.get_font(10, weight='light')       # 12 → 10 (-2)
        
        # Current time and date
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_date = now.strftime("%d.%m.%Y")
        weekday = now.strftime("%A")[:2].upper()  # Short weekday
        
        # Colors (for monochrome: 0=black, 255=white)
        BLACK = 0
        WHITE = 255
        
        # Layout constants
        margin = 8  # Increased margin to move content away from corners
        header_height = 24  # Increased for bigger time font
        
        # === HEADER SECTION ===
        # Header background
        draw.rectangle([0, 0, self.width, header_height], fill=BLACK)
        
        # Date and time in header (white text on black background)
        draw.text((margin, 3), f"{weekday} {current_date}", font=font_small, fill=WHITE)
        
        # Time on the right side - BIGGER FONT
        time_font = self.get_font(16, weight='bold')  # Bigger and bold for prominence
        time_bbox = draw.textbbox((0, 0), current_time, font=time_font)
        time_x = self.width - time_bbox[2] - margin
        draw.text((time_x, 2), current_time, font=time_font, fill=WHITE)
        
        # === MAIN CONTENT AREA ===
        content_y = header_height + 3
        
        # City name (no underline)
        city = weather_data.get('city', 'Unknown')
        draw.text((margin, content_y), city, font=font_title, fill=BLACK)
        
        # === LEFT COLUMN - TEMPERATURE AND WEATHER ===
        temp_y = content_y + 24  # More space from city name
        
        # Temperature (large and prominent)
        temp = weather_data.get('temperature', 0)
        temp_text = f"{temp:.0f}°"
        draw.text((margin, temp_y), temp_text, font=font_temp, fill=BLACK)
        
        # No weather icons - text only display
        
        # Weather description (positioned below temperature)
        description = weather_data.get('description', 'Unknown')
        if len(description) > 25:  # More space available without details panel
            description = description[:25] + "..."
        desc_y = temp_y + 38
        draw.text((margin, desc_y), description.title(), font=font_medium, fill=BLACK)
        
        # === RIGHT SIDE - WEATHER ICON ===
        # Visual Crossing Weather Icons 3rd Set (50x50px)
        weather_code = weather_data.get('weather_code', 0)
        is_day = weather_data.get('is_day', True)
        
        icon_size = 50
        icon_x = self.width - icon_size - margin
        icon_y = max(header_height + 2, (self.height - icon_size) // 2)  # Centered vertically on the right
        
        # Try to load Visual Crossing weather icon
        try:
            icon_filename = self.get_weather_icon_filename(weather_code, is_day)
            icon_image = self.load_png_icon(icon_filename, size=(icon_size, icon_size))
            
            if icon_image:
                # Paste the Visual Crossing weather icon
                image.paste(icon_image, (icon_x, icon_y))
                logger.debug(f"Loaded weather icon: {icon_filename}")
            else:
                logger.warning(f"Weather icon not found: {icon_filename}")
                
        except Exception as e:
            logger.debug(f"Could not load Visual Crossing icon: {e}")
        
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
