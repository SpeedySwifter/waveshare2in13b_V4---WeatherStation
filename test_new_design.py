#!/usr/bin/env python3
"""
Test script for the new weather display design
Creates a sample image to preview the improved interface
"""

import sys
import os
from datetime import datetime

# Add the current directory to the path
sys.path.append(os.path.dirname(__file__))

from display_manager import DisplayManager

def main():
    """Test the new display design with sample data"""
    print("Testing new weather display design...")
    
    # Create display manager
    display = DisplayManager()
    
    # Sample weather data for testing
    sample_weather_data = {
        'city': 'Stralsund',
        'country': 'DE',
        'temperature': 18.5,
        'feels_like': 16.2,
        'humidity': 72,
        'pressure': 1013.2,
        'description': 'Teilweise bewölkt',
        'weather_code': 2,  # Partly cloudy
        'is_day': True,
        'icon': '02d',
        'wind_speed': 12.3,
        'wind_direction': 245,
        'visibility': 10.0,
        'timestamp': datetime.now().isoformat()
    }
    
    print("Creating weather image with sample data:")
    print(f"  City: {sample_weather_data['city']}")
    print(f"  Temperature: {sample_weather_data['temperature']:.1f}°C")
    print(f"  Weather: {sample_weather_data['description']}")
    print(f"  Humidity: {sample_weather_data['humidity']}%")
    print(f"  Pressure: {sample_weather_data['pressure']:.0f} hPa")
    print(f"  Wind: {sample_weather_data['wind_speed']:.1f} m/s @ {sample_weather_data['wind_direction']}°")
    
    # Create and save the weather image
    try:
        image = display.create_weather_image(sample_weather_data)
        
        # Save the image for preview
        output_file = 'weather_display_new_design.png'
        image.save(output_file)
        print(f"\n✓ New design preview saved as: {output_file}")
        print("  Open this file to see the improved interface!")
        
        # Test different weather conditions with enhanced icons
        weather_conditions = [
            {'name': 'night_clear', 'is_day': False, 'weather_code': 0, 'description': 'Klarer Himmel', 'temp': 12.0},
            {'name': 'rain', 'is_day': True, 'weather_code': 63, 'description': 'Mäßiger Regen', 'temp': 15.5},
            {'name': 'snow', 'is_day': True, 'weather_code': 73, 'description': 'Mäßiger Schneefall', 'temp': -2.0},
            {'name': 'thunderstorm', 'is_day': False, 'weather_code': 95, 'description': 'Gewitter', 'temp': 18.0},
            {'name': 'fog', 'is_day': True, 'weather_code': 45, 'description': 'Nebel', 'temp': 8.5}
        ]
        
        for condition in weather_conditions:
            test_data = sample_weather_data.copy()
            test_data.update({
                'is_day': condition['is_day'],
                'weather_code': condition['weather_code'],
                'description': condition['description'],
                'temperature': condition['temp']
            })
            
            image_test = display.create_weather_image(test_data)
            output_file_test = f'weather_display_{condition["name"]}.png'
            image_test.save(output_file_test)
            print(f"✓ {condition['description']} preview saved as: {output_file_test}")
        
    except Exception as e:
        print(f"✗ Error creating weather image: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\nEnhanced icon features include:")
    print("  • Large ASCII art weather icons (sun, clouds, rain, snow, etc.)")
    print("  • Custom detail icons with Unicode symbols and ASCII fallbacks")
    print("  • Day/night weather variations")
    print("  • Multiple weather condition previews")
    print("  • Improved visual hierarchy with better symbols")
    print("  • E-ink optimized black/white graphics")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
