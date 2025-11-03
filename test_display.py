#!/usr/bin/env python3
"""
Simple E-Ink Display Test
Tests basic display functionality
"""

import sys
import os
import logging
from PIL import Image, ImageDraw, ImageFont

# Add the waveshare_epd directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'waveshare_epd'))

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_display():
    """Test the e-ink display"""
    print("🖥️  Testing E-Ink Display...")
    
    try:
        # Import display driver
        from waveshare_epd import epd2in13_V4
        print("✅ Display driver imported successfully")
        
        # Initialize display
        epd = epd2in13_V4.EPD()
        print("✅ Display object created")
        
        # Check SPI device
        if not os.path.exists('/dev/spidev0.0'):
            print("❌ SPI device /dev/spidev0.0 not found")
            return False
        print("✅ SPI device found")
        
        # Initialize display
        print("🔄 Initializing display...")
        epd.init()
        print("✅ Display initialized")
        
        # Clear display
        print("🔄 Clearing display...")
        epd.Clear()
        print("✅ Display cleared")
        
        # Create test image using official driver (handles rotation automatically)
        print("🔄 Creating test image...")
        # Create image with natural landscape dimensions (250x122)
        image = Image.new('1', (250, 122), 255)  # 1-bit image, white background
        draw = ImageDraw.Draw(image)
        
        # Draw test pattern for landscape layout
        draw.rectangle((5, 5, 245, 117), outline=0, width=2)
        draw.text((10, 15), "E-Ink Display Test", fill=0)
        draw.text((10, 35), "Weather Station Hardware", fill=0)
        draw.text((10, 55), "Official Waveshare Driver", fill=0)
        draw.text((10, 75), f"Display: {epd.width}x{epd.height}", fill=0)
        draw.text((10, 95), "Landscape Layout OK!", fill=0)
        
        # Display image
        print("🔄 Displaying test image...")
        epd.display(epd.getbuffer(image))
        print("✅ Test image displayed")
        
        # Sleep display
        print("🔄 Putting display to sleep...")
        epd.sleep()
        print("✅ Display sleeping")
        
        print("🎉 Display test completed successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import display driver: {e}")
        print("💡 Make sure waveshare_epd directory exists")
        return False
    except Exception as e:
        print(f"❌ Display test failed: {e}")
        print("💡 Check hardware connections and permissions")
        return False

def check_permissions():
    """Check user permissions"""
    print("🔍 Checking permissions...")
    
    import grp
    import pwd
    
    # Get current user
    user = pwd.getpwuid(os.getuid()).pw_name
    print(f"Current user: {user}")
    
    # Check groups
    groups = [g.gr_name for g in grp.getgrall() if user in g.gr_mem]
    user_groups = os.getgroups()
    group_names = [grp.getgrgid(gid).gr_name for gid in user_groups]
    
    print(f"User groups: {', '.join(group_names)}")
    
    if 'spi' in group_names:
        print("✅ User is in 'spi' group")
    else:
        print("❌ User is NOT in 'spi' group")
        print("💡 Run: sudo usermod -a -G spi,gpio $USER")
        print("💡 Then log out and back in")
    
    if 'gpio' in group_names:
        print("✅ User is in 'gpio' group")
    else:
        print("❌ User is NOT in 'gpio' group")

if __name__ == "__main__":
    print("=== E-Ink Display Hardware Test ===")
    print()
    
    check_permissions()
    print()
    
    success = test_display()
    
    if not success:
        print()
        print("🔧 Troubleshooting Tips:")
        print("1. Check all hardware connections")
        print("2. Ensure SPI is enabled: sudo raspi-config")
        print("3. Add user to groups: sudo usermod -a -G spi,gpio $USER")
        print("4. Reboot after group changes")
        print("5. Check display power (3.3V)")
        sys.exit(1)
    else:
        print()
        print("✅ Display hardware is working correctly!")
