#!/bin/bash

# Setup script for Raspberry Pi Weather Station with Open-Meteo API
# No API key required - uses free Open-Meteo weather service
# Run with: bash setup.sh

echo "=== Raspberry Pi Weather Station Setup (Open-Meteo API) ==="
echo

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "Warning: This doesn't appear to be a Raspberry Pi"
    echo "Some features may not work correctly."
    echo
fi

# Update system
echo "1. Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required system packages (including Waveshare recommendations)
echo "2. Installing required packages..."
sudo apt install -y python3 python3-pip python3-venv git python3-dev \
    libjpeg-dev zlib1g-dev libfreetype-dev liblcms2-dev libopenjp2-7-dev libtiff-dev \
    python3-pil python3-numpy python3-requests python3-rpi.gpio python3-spidev python3-gpiozero

# Install Python dependencies
echo "3. Installing Python dependencies..."
# Try system packages first, then fallback to pip with --break-system-packages if needed
if ! python3 -c "import requests, RPi.GPIO, spidev" 2>/dev/null; then
    echo "Installing additional packages with pip..."
    pip3 install --break-system-packages requests RPi.GPIO spidev 2>/dev/null || echo "Some packages may need manual installation"
fi

# Enable SPI
echo "4. Enabling SPI interface..."
if ! grep -q "dtparam=spi=on" /boot/config.txt; then
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
    echo "SPI enabled in /boot/config.txt"
else
    echo "SPI already enabled"
fi

# Add user to spi and gpio groups
echo "5. Adding user to spi and gpio groups..."
sudo usermod -a -G spi,gpio $USER

# Create config file if it doesn't exist
echo "6. Setting up configuration..."
if [ ! -f config.json ]; then
    echo "Creating default config.json..."
    cat > config.json << EOF
{
    "latitude": 54.3091,
    "longitude": 13.0818,
    "city": "Stralsund",
    "country_code": "DE",
    "update_interval": 30,
    "display_rotation": 0,
    "language": "de",
    "units": "metric"
}
EOF
    echo "Created config.json with default settings"
    echo "Edit config.json to customize your location coordinates"
else
    echo "config.json already exists"
fi

# Install systemd service
echo "7. Installing systemd service..."
sudo cp weather-station.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable weather-station.service

echo
echo "=== Setup Complete! ==="
echo
echo "Next steps:"
echo "1. Edit config.json to customize your location (latitude/longitude)"
echo "2. Connect your Waveshare 2.13\" V4 display"
echo "3. Reboot your Raspberry Pi: sudo reboot"
echo "4. Test hardware setup: python3 hardware_test.py"
echo "5. Start the service: sudo systemctl start weather-station.service"
echo "6. Check status: sudo systemctl status weather-station.service"
echo
echo "For manual testing: python3 weather_station.py"
echo "For hardware verification: python3 hardware_test.py"
echo
