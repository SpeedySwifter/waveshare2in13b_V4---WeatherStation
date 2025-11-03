#!/usr/bin/env python3
"""
Create sample monochrome weather icons for testing
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_sample_icons():
    """Create basic monochrome weather icons with simple shapes"""
    icon_size = 50
    icons_dir = "visual_crossing_icons"
    
    # Ensure directory exists
    os.makedirs(icons_dir, exist_ok=True)
    
    print("Creating sample monochrome weather icons...")
    
    # Create each icon with simple geometric shapes
    icons_to_create = [
        ("clear-day.png", "sun"),
        ("clear-night.png", "moon"),
        ("partly-cloudy-day.png", "partly_cloudy"),
        ("partly-cloudy-night.png", "cloudy"),
        ("cloudy.png", "cloudy"),
        ("fog.png", "fog"),
        ("rain.png", "rain"),
        ("drizzle.png", "drizzle"),
        ("snow.png", "snow"),
        ("thunderstorms.png", "thunder"),
        ("thunderstorms-rain.png", "thunder_rain")
    ]
    
    for filename, icon_type in icons_to_create:
        # Create a new image with white background
        image = Image.new('L', (icon_size, icon_size), 255)  # Grayscale, white background
        draw = ImageDraw.Draw(image)
        
        center_x, center_y = icon_size // 2, icon_size // 2
        
        if icon_type == "sun":
            # Draw sun - circle with rays
            draw.ellipse([15, 15, 35, 35], fill=0)  # Black circle
            # Rays
            for angle in range(0, 360, 45):
                import math
                x1 = center_x + 20 * math.cos(math.radians(angle))
                y1 = center_y + 20 * math.sin(math.radians(angle))
                x2 = center_x + 24 * math.cos(math.radians(angle))
                y2 = center_y + 24 * math.sin(math.radians(angle))
                draw.line([(x1, y1), (x2, y2)], fill=0, width=2)
                
        elif icon_type == "moon":
            # Draw crescent moon
            draw.ellipse([15, 15, 35, 35], fill=0)  # Black circle
            draw.ellipse([20, 15, 40, 35], fill=255)  # White circle to create crescent
            
        elif icon_type in ["cloudy", "partly_cloudy"]:
            # Draw cloud shapes
            draw.ellipse([10, 20, 25, 30], fill=0)  # Left cloud part
            draw.ellipse([20, 15, 35, 25], fill=0)  # Middle cloud part
            draw.ellipse([30, 20, 40, 30], fill=0)  # Right cloud part
            draw.rectangle([15, 22, 35, 30], fill=0)  # Connect the clouds
            
        elif icon_type == "fog":
            # Draw horizontal lines for fog
            for y in range(15, 35, 4):
                draw.line([(10, y), (40, y)], fill=0, width=2)
                
        elif icon_type in ["rain", "drizzle", "thunder_rain"]:
            # Draw cloud
            draw.ellipse([15, 10, 35, 20], fill=0)
            # Draw rain drops
            for x in range(18, 35, 6):
                draw.line([(x, 25), (x, 35)], fill=0, width=2)
                
        elif icon_type == "snow":
            # Draw cloud
            draw.ellipse([15, 10, 35, 20], fill=0)
            # Draw snowflakes (simple crosses)
            for x in range(18, 35, 8):
                for y in range(25, 35, 5):
                    draw.line([(x-2, y), (x+2, y)], fill=0, width=1)
                    draw.line([(x, y-2), (x, y+2)], fill=0, width=1)
                    
        elif icon_type in ["thunder", "thunder_rain"]:
            # Draw cloud
            draw.ellipse([15, 8, 35, 18], fill=0)
            # Draw lightning bolt
            draw.polygon([(25, 20), (28, 25), (26, 25), (29, 32), (23, 28), (25, 28), (22, 22)], fill=0)
        
        # Convert to 1-bit and save
        image = image.point(lambda x: 0 if x < 128 else 255, mode='1')
        icon_path = os.path.join(icons_dir, filename)
        image.save(icon_path)
        print(f"✓ Created: {filename}")
    
    print(f"\n✓ Created {len(icons_to_create)} sample weather icons in {icons_dir}/")
    print("These are geometric shape icons optimized for e-ink displays.")

if __name__ == "__main__":
    create_sample_icons()
