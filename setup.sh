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

# SSH Configuration Fix for Raspberry Pi Zero 2
echo "6. Configuring SSH for Raspberry Pi Zero 2..."

# Enable SSH service
echo "   - Enabling SSH service..."
sudo systemctl enable ssh
sudo systemctl start ssh

# Create SSH directory if it doesn't exist
if [ ! -d "/home/$USER/.ssh" ]; then
    mkdir -p /home/$USER/.ssh
    chmod 700 /home/$USER/.ssh
    chown $USER:$USER /home/$USER/.ssh
fi

# Fix SSH configuration for better compatibility
echo "   - Optimizing SSH configuration..."
sudo tee -a /etc/ssh/sshd_config.d/99-pi-zero-2-fix.conf > /dev/null << EOF
# SSH Configuration fixes for Raspberry Pi Zero 2
# Improve connection stability and compatibility

# Allow password authentication (can be disabled later for security)
PasswordAuthentication yes
PubkeyAuthentication yes

# Increase connection limits
MaxAuthTries 6
MaxSessions 10

# Optimize for slower hardware
LoginGraceTime 120
ClientAliveInterval 60
ClientAliveCountMax 3

# Enable compression to help with slower connections
Compression yes

# Allow root login with key only (more secure)
PermitRootLogin prohibit-password

# Disable DNS lookups to speed up connections
UseDNS no

# Set proper ciphers for Pi Zero 2 performance
Ciphers aes128-ctr,aes192-ctr,aes256-ctr,aes128-gcm@openssh.com,aes256-gcm@openssh.com
MACs hmac-sha2-256,hmac-sha2-512,hmac-sha1

# Keep connections alive
TCPKeepAlive yes
EOF

# Restart SSH service to apply changes
echo "   - Restarting SSH service..."
sudo systemctl restart ssh

# Check if SSH is running
if sudo systemctl is-active --quiet ssh; then
    echo "   ✓ SSH service is running"
else
    echo "   ⚠ SSH service failed to start - check logs with: sudo journalctl -u ssh"
fi

# Display SSH connection info
echo "   - SSH connection information:"
echo "     Default username: $USER"
echo "     SSH port: 22"
echo "     To connect: ssh $USER@<pi-ip-address>"
echo "     Find IP with: hostname -I"

# Create config file if it doesn't exist
echo "7. Setting up configuration..."
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
echo "8. Installing systemd service..."
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
