#!/bin/bash

# Weather Station Auto-Start Installation Script
# This script sets up robust auto-start that survives reboots and crashes

echo "=== Weather Station Auto-Start Setup ==="
echo

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please run this script as regular user (not sudo)"
    echo "The script will ask for sudo when needed"
    exit 1
fi

# Get current directory and user
INSTALL_DIR="$(pwd)"
CURRENT_USER="$(whoami)"

echo "📍 Installation directory: $INSTALL_DIR"
echo "👤 User: $CURRENT_USER"
echo

# Update the service file with correct paths
echo "🔧 Configuring service file..."
sed -i "s|/home/pi/weather-station|$INSTALL_DIR|g" weather-station.service
sed -i "s|User=pi|User=$CURRENT_USER|g" weather-station.service
sed -i "s|Group=pi|Group=$CURRENT_USER|g" weather-station.service

# Install the systemd service
echo "📦 Installing systemd service..."
sudo cp weather-station.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable the service for auto-start
echo "🚀 Enabling auto-start..."
sudo systemctl enable weather-station.service

# Add user to required groups
echo "👥 Adding user to required groups..."
sudo usermod -a -G spi,gpio,i2c "$CURRENT_USER"

# Create log directory
echo "📝 Setting up logging..."
sudo mkdir -p /var/log/weather-station
sudo chown "$CURRENT_USER:$CURRENT_USER" /var/log/weather-station

# Create a watchdog script for extra reliability
echo "🐕 Creating watchdog script..."
cat > weather_watchdog.sh << 'EOF'
#!/bin/bash

# Weather Station Watchdog Script
# Monitors the weather station and restarts if needed

LOG_FILE="/var/log/weather-station/watchdog.log"
SERVICE_NAME="weather-station.service"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Check if service is running
if ! systemctl is-active --quiet "$SERVICE_NAME"; then
    log_message "WARNING: Weather station service is not running. Attempting restart..."
    sudo systemctl start "$SERVICE_NAME"
    
    # Wait a bit and check again
    sleep 10
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        log_message "SUCCESS: Weather station service restarted successfully"
    else
        log_message "ERROR: Failed to restart weather station service"
    fi
else
    log_message "INFO: Weather station service is running normally"
fi

# Check system resources
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)

log_message "STATS: Memory usage: ${MEMORY_USAGE}%, CPU usage: ${CPU_USAGE}%"

# Clean old logs (keep last 100 lines)
if [ -f "$LOG_FILE" ]; then
    tail -n 100 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
fi
EOF

chmod +x weather_watchdog.sh

# Create cron job for watchdog (runs every 5 minutes)
echo "⏰ Setting up watchdog cron job..."
(crontab -l 2>/dev/null; echo "*/5 * * * * $INSTALL_DIR/weather_watchdog.sh") | crontab -

# Create startup script for additional reliability
echo "🔄 Creating startup script..."
cat > weather_startup.sh << 'EOF'
#!/bin/bash

# Weather Station Startup Script
# Ensures the weather station starts properly after boot

# Wait for network to be ready
echo "Waiting for network connection..."
while ! ping -c 1 8.8.8.8 &> /dev/null; do
    sleep 5
done

# Wait for SPI to be available
echo "Waiting for SPI interface..."
while [ ! -e /dev/spidev0.0 ]; do
    sleep 2
done

# Start the weather station service
echo "Starting weather station service..."
sudo systemctl start weather-station.service

echo "Weather station startup complete!"
EOF

chmod +x weather_startup.sh

# Add startup script to cron (runs at boot)
(crontab -l 2>/dev/null; echo "@reboot sleep 30 && $INSTALL_DIR/weather_startup.sh") | crontab -

# Test the service
echo "🧪 Testing the service..."
sudo systemctl start weather-station.service
sleep 5

if systemctl is-active --quiet weather-station.service; then
    echo "✅ Service is running successfully!"
else
    echo "⚠️  Service may have issues. Check logs with:"
    echo "   sudo journalctl -u weather-station.service -f"
fi

echo
echo "=== Auto-Start Setup Complete! ==="
echo
echo "🎉 Your weather station will now:"
echo "   ✅ Start automatically after boot"
echo "   ✅ Restart automatically if it crashes"
echo "   ✅ Survive system reboots and power outages"
echo "   ✅ Be monitored by watchdog every 5 minutes"
echo "   ✅ Log all activities for debugging"
echo
echo "📋 Useful commands:"
echo "   Status:    sudo systemctl status weather-station.service"
echo "   Stop:      sudo systemctl stop weather-station.service"
echo "   Start:     sudo systemctl start weather-station.service"
echo "   Restart:   sudo systemctl restart weather-station.service"
echo "   Logs:      sudo journalctl -u weather-station.service -f"
echo "   Watchdog:  tail -f /var/log/weather-station/watchdog.log"
echo
echo "🔄 Reboot your Pi to test the auto-start: sudo reboot"
