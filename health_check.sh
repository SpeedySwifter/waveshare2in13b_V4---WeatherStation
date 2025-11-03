#!/bin/bash

# Weather Station Health Check Script
# Diagnoses and fixes common issues automatically

echo "=== Weather Station Health Check ==="
echo

ISSUES_FOUND=0
FIXES_APPLIED=0

# Function to log issues
log_issue() {
    echo "❌ ISSUE: $1"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
}

log_fix() {
    echo "🔧 FIX: $1"
    FIXES_APPLIED=$((FIXES_APPLIED + 1))
}

log_ok() {
    echo "✅ OK: $1"
}

# Check 1: SPI Interface
echo "🔍 Checking SPI interface..."
if [ -e /dev/spidev0.0 ]; then
    log_ok "SPI device found"
else
    log_issue "SPI device not found"
    if grep -q "dtparam=spi=on" /boot/config.txt; then
        log_issue "SPI enabled in config but device missing - may need reboot"
    else
        log_fix "Enabling SPI in /boot/config.txt"
        echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
        FIXES_APPLIED=$((FIXES_APPLIED + 1))
    fi
fi

# Check 2: Network connectivity
echo "🔍 Checking network connectivity..."
if ping -c 1 8.8.8.8 &> /dev/null; then
    log_ok "Internet connection available"
else
    log_issue "No internet connection - weather data cannot be fetched"
fi

# Check 3: Service status
echo "🔍 Checking service status..."
if systemctl is-active --quiet weather-station.service; then
    log_ok "Weather station service is running"
else
    log_issue "Weather station service is not running"
    log_fix "Starting weather station service"
    sudo systemctl start weather-station.service
    sleep 3
    if systemctl is-active --quiet weather-station.service; then
        log_ok "Service started successfully"
    else
        log_issue "Failed to start service - check logs"
    fi
fi

# Check 4: Configuration file
echo "🔍 Checking configuration..."
if [ -f "config.json" ]; then
    if grep -q "YOUR_OPENWEATHERMAP_API_KEY_HERE" config.json 2>/dev/null; then
        log_issue "API key not configured in config.json"
    else
        log_ok "Configuration file exists with API key"
    fi
else
    log_issue "Configuration file missing"
    if [ -f "config.json.example" ]; then
        log_fix "Creating config.json from example"
        cp config.json.example config.json
    fi
fi

# Check 5: Python dependencies
echo "🔍 Checking Python dependencies..."
MISSING_DEPS=""
for dep in "requests" "PIL" "RPi.GPIO" "spidev"; do
    if ! python3 -c "import $dep" 2>/dev/null; then
        MISSING_DEPS="$MISSING_DEPS $dep"
    fi
done

if [ -z "$MISSING_DEPS" ]; then
    log_ok "All Python dependencies available"
else
    log_issue "Missing Python dependencies:$MISSING_DEPS"
    log_fix "Installing missing dependencies"
    sudo apt update
    sudo apt install -y python3-requests python3-pil python3-rpi.gpio python3-spidev
fi

# Check 6: File permissions
echo "🔍 Checking file permissions..."
if [ -r "weather_station.py" ] && [ -x "weather_station.py" ]; then
    log_ok "Main script has correct permissions"
else
    log_issue "Main script permissions incorrect"
    log_fix "Fixing file permissions"
    chmod +x weather_station.py
fi

# Check 7: User groups
echo "🔍 Checking user groups..."
CURRENT_USER=$(whoami)
if groups "$CURRENT_USER" | grep -q "spi\|gpio"; then
    log_ok "User is in required groups (spi, gpio)"
else
    log_issue "User not in required groups"
    log_fix "Adding user to spi and gpio groups"
    sudo usermod -a -G spi,gpio "$CURRENT_USER"
    echo "⚠️  You need to log out and back in for group changes to take effect"
fi

# Check 8: System resources
echo "🔍 Checking system resources..."
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2 * 100.0)}')
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')

if [ "$MEMORY_USAGE" -lt 80 ]; then
    log_ok "Memory usage: ${MEMORY_USAGE}%"
else
    log_issue "High memory usage: ${MEMORY_USAGE}%"
fi

if [ "$DISK_USAGE" -lt 90 ]; then
    log_ok "Disk usage: ${DISK_USAGE}%"
else
    log_issue "High disk usage: ${DISK_USAGE}%"
fi

# Check 9: Log files
echo "🔍 Checking log files..."
if [ -f "weather_station.log" ]; then
    LOG_SIZE=$(du -k weather_station.log | cut -f1)
    if [ "$LOG_SIZE" -gt 10240 ]; then  # 10MB
        log_fix "Rotating large log file"
        tail -n 1000 weather_station.log > weather_station.log.tmp
        mv weather_station.log.tmp weather_station.log
    else
        log_ok "Log file size acceptable"
    fi
fi

# Check 10: Recent errors
echo "🔍 Checking for recent errors..."
if [ -f "weather_station.log" ]; then
    ERROR_COUNT=$(grep -c "ERROR" weather_station.log | tail -1)
    if [ "$ERROR_COUNT" -gt 10 ]; then
        log_issue "Many errors found in log file ($ERROR_COUNT)"
        echo "   Recent errors:"
        grep "ERROR" weather_station.log | tail -3 | sed 's/^/   /'
    else
        log_ok "No significant errors in log"
    fi
fi

echo
echo "=== Health Check Summary ==="
echo "🔍 Issues found: $ISSUES_FOUND"
echo "🔧 Fixes applied: $FIXES_APPLIED"

if [ "$ISSUES_FOUND" -eq 0 ]; then
    echo "🎉 All systems healthy!"
elif [ "$FIXES_APPLIED" -gt 0 ]; then
    echo "🔧 Some issues were fixed automatically"
    echo "💡 Consider rebooting if SPI or group changes were made"
else
    echo "⚠️  Issues found that require manual attention"
fi

echo
echo "📋 Quick commands:"
echo "   Service status: sudo systemctl status weather-station.service"
echo "   View logs:      tail -f weather_station.log"
echo "   Test manually:  python3 weather_station.py"
