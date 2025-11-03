#!/bin/bash

# Install Weather Station Service Script
# Run this on your Raspberry Pi to install the systemd service

echo "=== Installing Weather Station Service ==="

# Get current user and working directory
CURRENT_USER=$(whoami)
CURRENT_DIR=$(pwd)

echo "Current user: $CURRENT_USER"
echo "Project directory: $CURRENT_DIR"

# Create a temporary service file with correct paths
cat > weather-station-temp.service << EOF
[Unit]
Description=Raspberry Pi Weather Station with E-Ink Display
Documentation=https://github.com/SpeedySwifter/waveshare2in13b_V4---WeatherStation
After=network-online.target
Wants=network-online.target
StartLimitIntervalSec=300
StartLimitBurst=5

[Service]
Type=simple
User=$CURRENT_USER
Group=$CURRENT_USER
WorkingDirectory=$CURRENT_DIR
ExecStart=/usr/bin/python3 $CURRENT_DIR/weather_station.py
ExecReload=/bin/kill -HUP \$MAINPID

# Restart configuration - very robust
Restart=always
RestartSec=15
TimeoutStartSec=60
TimeoutStopSec=30

# Failure handling
StartLimitAction=restart
FailureAction=restart

# Process management
KillMode=mixed
KillSignal=SIGTERM
SendSIGKILL=yes
FinalKillSignal=SIGKILL

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=weather-station

# Security and resource limits
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ReadWritePaths=$CURRENT_DIR
MemoryMax=256M
CPUQuota=50%

# Environment variables
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# Install the service
echo "Installing systemd service..."
sudo cp weather-station-temp.service /etc/systemd/system/weather-station.service
rm weather-station-temp.service

# Reload systemd and enable service
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload

echo "Enabling weather-station service..."
sudo systemctl enable weather-station.service

echo "Starting weather-station service..."
sudo systemctl start weather-station.service

# Check status
echo ""
echo "=== Service Status ==="
sudo systemctl status weather-station.service --no-pager

echo ""
echo "=== Installation Complete! ==="
echo ""
echo "Useful commands:"
echo "  Check status:    sudo systemctl status weather-station.service"
echo "  View logs:       sudo journalctl -u weather-station.service -f"
echo "  Restart service: sudo systemctl restart weather-station.service"
echo "  Stop service:    sudo systemctl stop weather-station.service"
echo "  Disable service: sudo systemctl disable weather-station.service"
echo ""
