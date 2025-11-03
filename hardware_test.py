#!/usr/bin/env python3
"""
Hardware Test Script for Waveshare 2.13inch e-Paper HAT V4
Based on official Waveshare demo pattern for hardware verification
"""

import sys
import os
import logging
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

# Add the waveshare_epd directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'waveshare_epd'))

try:
    from waveshare_epd import epd2in13_V4
    print("✓ Waveshare EPD module imported successfully")
except ImportError as e:
    print(f"✗ Failed to import Waveshare EPD module: {e}")
    print("Make sure the waveshare_epd directory contains epd2in13_V4.py")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_system_requirements():
    """Check system requirements and dependencies"""
    print("\n=== System Requirements Check ===")
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version < (3, 6):
        print("✗ Python 3.6+ required")
        return False
    else:
        print("✓ Python version OK")
    
    # Check required modules
    required_modules = ['spidev', 'RPi.GPIO', 'PIL']
    for module in required_modules:
        try:
            __import__(module)
            print(f"✓ {module} module available")
        except ImportError:
            print(f"✗ {module} module missing - install with: pip3 install {module}")
            return False
    
    # Check SPI devices
    import glob
    spi_devices = glob.glob('/dev/spidev*')
    if spi_devices:
        print(f"✓ SPI devices found: {spi_devices}")
    else:
        print("✗ No SPI devices found")
        print("  Enable SPI with: sudo raspi-config → Interfacing Options → SPI → Yes")
        return False
    
    # Check boot config
    try:
        with open('/boot/config.txt', 'r') as f:
            if 'dtparam=spi=on' in f.read():
                print("✓ SPI enabled in boot config")
            else:
                print("✗ SPI not enabled in boot config")
                return False
    except (FileNotFoundError, PermissionError):
        print("⚠ Could not verify boot config (may not be on Raspberry Pi)")
    
    return True

def create_test_image():
    """Create a test image similar to official Waveshare demo"""
    print("\n=== Creating Test Image ===")
    
    # Display dimensions
    width = 122
    height = 250
    
    # Create image
    image = Image.new('1', (width, height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)
    
    try:
        font18 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 18)
        font14 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 14)
        font12 = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 12)
    except:
        font18 = ImageFont.load_default()
        font14 = ImageFont.load_default()
        font12 = ImageFont.load_default()
        print("⚠ Using default font (system fonts not found)")
    
    # Draw test pattern
    y = 5
    
    # Title
    draw.text((5, y), 'Hardware Test', font=font18, fill=0)
    y += 25
    
    # Timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    draw.text((5, y), timestamp, font=font12, fill=0)
    y += 20
    
    # Test patterns
    draw.line([(5, y), (width-5, y)], fill=0, width=2)
    y += 10
    
    draw.text((5, y), 'Waveshare 2.13" V4', font=font14, fill=0)
    y += 20
    
    draw.text((5, y), 'Black/White Display', font=font12, fill=0)
    y += 20
    
    # Draw rectangles
    draw.rectangle([(5, y), (width-5, y+20)], outline=0, width=2)
    y += 30
    
    # Draw filled rectangle
    draw.rectangle([(5, y), (50, y+15)], fill=0)
    draw.text((55, y), 'Filled rect', font=font12, fill=0)
    y += 25
    
    # Draw circle
    draw.ellipse([(5, y), (25, y+20)], outline=0, width=2)
    draw.text((30, y+5), 'Circle', font=font12, fill=0)
    y += 30
    
    # Status
    draw.text((5, y), 'Test Pattern OK', font=font14, fill=0)
    
    print("✓ Test image created successfully")
    return image

def test_display_hardware():
    """Test the e-paper display hardware"""
    print("\n=== Hardware Display Test ===")
    
    try:
        # Initialize display
        epd = epd2in13_V4.EPD()
        print("✓ EPD object created")
        
        # Initialize the display
        epd.init()
        print("✓ Display initialized")
        
        # Clear display
        print("Clearing display...")
        epd.Clear()
        print("✓ Display cleared")
        
        # Create and display test image
        image = create_test_image()
        
        print("Displaying test image...")
        buffer = epd.getbuffer(image)
        epd.display(buffer)
        print("✓ Test image displayed")
        
        # Save image for reference
        image.save('hardware_test_image.png')
        print("✓ Test image saved as hardware_test_image.png")
        
        # Sleep display
        print("Putting display to sleep...")
        epd.sleep()
        print("✓ Display put to sleep")
        
        return True
        
    except Exception as e:
        print(f"✗ Hardware test failed: {e}")
        logger.error(f"Hardware test error: {e}", exc_info=True)
        return False

def main():
    """Main test function"""
    print("Waveshare 2.13inch e-Paper HAT V4 Hardware Test")
    print("=" * 50)
    
    # Check system requirements
    if not check_system_requirements():
        print("\n✗ System requirements check failed")
        print("Please fix the issues above before running the hardware test")
        return False
    
    # Test display hardware
    if not test_display_hardware():
        print("\n✗ Hardware test failed")
        print("Check connections and ensure the display is properly connected")
        return False
    
    print("\n" + "=" * 50)
    print("✓ All tests passed successfully!")
    print("Your Waveshare 2.13inch e-Paper HAT V4 is working correctly")
    print("You can now run your weather station with confidence")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
