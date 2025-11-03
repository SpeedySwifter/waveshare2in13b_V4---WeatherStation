# Raspberry Pi Weather Station with Waveshare 2.13" V4 E-Ink Display

A weather station for Raspberry Pi Zero 2 with Waveshare 2.13" V4 E-Ink Display that fetches weather data from the free Open-Meteo API.

**🇩🇪 [Deutsche Version / German Version](README_DE.md)**

## Features

- **E-Ink Display**: Uses Waveshare 2.13" V4 Display (black/white)
- **Weather API**: Fetches current weather data from Open-Meteo (free, no API key required)
- **German Language**: Supports German weather reports
- **Energy Efficient**: E-Ink display only consumes power during updates
- **Automatic Updates**: Configurable update intervals
- **Robust Error Handling**: Logging and recovery on errors

## Hardware Requirements

- **Raspberry Pi Zero 2 W**
- **Waveshare 2.13inch e-Paper HAT V4** (Black/White display)
- **MicroSD Card** (16GB+ recommended, Class 10)
- **Power Supply** (Micro-USB, 5V/2.5A minimum recommended)
- **Internet Connection** (Wi-Fi for weather data)

## Display Layout

The 2.13" display (250x122 pixels) features a modern, clean design with:

### **Header Section**
- **Black header bar** with white text
- **Date and weekday** (left side)
- **Current time** (right side)

### **Main Content**
- **City name** with decorative underline
- **Large temperature** display (prominent)
- **Weather icon** (Unicode symbols for different conditions)
- **Weather description** in German

### **Details Panel**
- **Bordered information box** with:
  - 💧 **Humidity** percentage
  - 📊 **Air pressure** in hPa
  - 💨 **Wind speed** in m/s
  - 🧭 **Wind direction** in degrees

### **Design Features**
- **Professional PNG weather icons** with ASCII art fallback
- **Merriweather Sans typography** with multiple font weights
- **Day/night weather variations** (sun/moon based on time)
- **Typography hierarchy** with proper font weights (light, regular, medium, semibold, bold)
- **Decorative corner elements**
- **Clean borders and separators**
- **Optimized for e-ink display** (black/white only)
- **No external dependencies** for icons (PNG format)

### **Weather Icons**
The system uses high-quality PNG icons from the `icons png/` folder:
- **Clear sky**: Different icons for day (sun) and night (moon)
- **Cloudy conditions**: Various cloud densities (1-3 levels)
- **Precipitation**: Rain, snow, and mixed conditions
- **Special weather**: Fog, thunderstorms, severe weather
- **No dependencies**: PNG format works everywhere
- **Automatic fallback**: ASCII art if icons unavailable

### **Typography**
Professional Merriweather Sans font family with multiple weights:
- **Light**: Small details and secondary information
- **Regular**: Standard text and labels
- **Medium**: Weather descriptions and medium emphasis
- **SemiBold**: City names and section headers
- **Bold**: Large temperature display and primary emphasis
- **Automatic fallback**: System fonts if Merriweather Sans unavailable

## Quick Start

For quick installation, use the automatic setup script:

```bash
# Clone project
git clone https://github.com/SpeedySwifter/waveshare2in13b_V4---WeatherStation.git weather-station
cd weather-station

# Run automatic setup
bash setup.sh

# Adjust coordinates in config.json (optional)
nano config.json

# Reboot system
sudo reboot
```

## Detailed Installation

### 1. Clone Project

```bash
git clone https://github.com/SpeedySwifter/waveshare2in13b_V4---WeatherStation.git weather-station
cd weather-station
```

### 2. Prepare Raspberry Pi OS

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install git (if not present)
sudo apt install -y git
```

### 3. Install Dependencies

```bash
# Install Python and required packages
sudo apt install -y python3 python3-pip python3-venv git python3-dev libjpeg-dev zlib1g-dev libfreetype-dev liblcms2-dev libopenjp2-7-dev libtiff-dev python3-pil python3-requests python3-rpi.gpio python3-spidev

# Enable SPI
sudo raspi-config
# Interface Options -> SPI -> Enable

# Add user to groups
sudo usermod -a -G spi,gpio $USER
```

### 4. Configuration

Copy the example configuration and customize it:

```bash
cp config.json.example config.json
```

Edit `config.json` and adjust coordinates for your location:

```json
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
```

**Finding Coordinates:**
- Use [OpenStreetMap](https://www.openstreetmap.org/) or Google Maps
- Click on your desired location
- Copy the Latitude and Longitude values

### 5. Hardware Connection

Connect the Waveshare 2.13" V4 Display to the Raspberry Pi:

| Display Pin | Pi Pin | Function |
|-------------|--------|----------|
| VCC | 3.3V | Power Supply |
| GND | GND | Ground |
| DIN | GPIO 10 (MOSI) | SPI Data |
| CLK | GPIO 11 (SCLK) | SPI Clock |
| CS | GPIO 8 (CE0) | Chip Select |
| DC | GPIO 25 | Data/Command |
| RST | GPIO 17 | Reset |
| BUSY | GPIO 24 | Busy Signal |

## Usage

### Manual Start

```bash
python3 weather_station.py
```

### Install as Service

```bash
# Install service
sudo cp weather-station.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable weather-station.service

# Start service
sudo systemctl start weather-station.service

# Check status
sudo systemctl status weather-station.service
```

### Manage Service

```bash
# Stop service
sudo systemctl stop weather-station.service

# Restart service
sudo systemctl restart weather-station.service

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable weather-station.service
sudo systemctl start weather-station.service
```

## Configuration

### config.json Parameters

- **latitude**: Location latitude (e.g. 54.3091)
- **longitude**: Location longitude (e.g. 13.0818)
- **city**: City for display (e.g. "Stralsund", "Berlin")
- **country_code**: Country code (e.g. "DE")
- **update_interval**: Update interval in minutes (default: 30)
- **display_rotation**: Display rotation in degrees (0, 90, 180, 270)
- **language**: Language for weather descriptions ("de", "en")
- **units**: Units ("metric" for Celsius, "imperial" for Fahrenheit)

## Additional Scripts

### setup.sh
Automatic setup script for complete installation:
```bash
bash setup.sh
```

### ssh_fix.sh
Standalone SSH configuration fix for Raspberry Pi Zero 2:
```bash
bash ssh_fix.sh
```

### test_new_design.py
Preview the modern display design without hardware:
```bash
python3 test_new_design.py
```

### install_svg_support.sh
~~Install SVG icon support~~ (No longer needed - PNG icons used):
```bash
# bash install_svg_support.sh  # Not needed anymore
```

### health_check.sh
Checks weather station status and restarts if needed:
```bash
bash health_check.sh
```

## Project Structure

```
weather-station/
├── weather_station.py          # Main program
├── weather_api.py             # Open-Meteo API interface
├── display_manager.py         # E-Ink display management (modern design)
├── config.py                  # Configuration loader
├── config.json.example        # Example configuration
├── requirements.txt           # Python dependencies
├── weather-station.service    # Systemd service
├── setup.sh                   # Automatic setup
├── ssh_fix.sh                 # SSH configuration fix for Pi Zero 2
├── test_new_design.py         # Design preview generator
├── install_svg_support.sh     # SVG icon support installer (legacy)
├── health_check.sh           # Status monitoring
├── icons png/                # PNG weather icon assets
├── Merriweather_Sans/        # Professional font family
├── waveshare_epd/            # Display drivers
├── README.md                 # English documentation
├── README_DE.md              # German documentation
└── .gitignore               # Git ignore rules
```

## Logs and Debugging

Logs are stored in `weather_station.log`:

```bash
# View live logs
tail -f weather_station.log

# View service logs
sudo journalctl -u weather-station.service -f

# Show recent errors
sudo journalctl -u weather-station.service --since "1 hour ago"
```

### Common Issues

1. **SPI not enabled**: `sudo raspi-config` → Interface Options → SPI → Enable
2. **Permission errors**: Add user to groups: `sudo usermod -a -G spi,gpio $USER`
3. **Display shows nothing**: Check hardware connections
4. **Service won't start**: Check logs: `sudo journalctl -u weather-station.service`

### SSH Troubleshooting (Raspberry Pi Zero 2)

The setup script automatically configures SSH for optimal performance on Raspberry Pi Zero 2. For standalone SSH fixes, you can also run:

```bash
bash ssh_fix.sh
```

If you encounter SSH connection issues:

#### **SSH Connection Problems**
```bash
# Check if SSH service is running
sudo systemctl status ssh

# Restart SSH service
sudo systemctl restart ssh

# Enable SSH if disabled
sudo systemctl enable ssh
sudo systemctl start ssh
```

#### **Find Your Pi's IP Address**
```bash
# On the Pi itself
hostname -I

# From your router's admin panel
# Look for "raspberrypi" or your custom hostname

# Network scan from another device
nmap -sn 192.168.1.0/24  # Adjust subnet as needed
```

#### **Connection Commands**
```bash
# Basic SSH connection
ssh pi@<pi-ip-address>

# With specific port (if changed)
ssh -p 22 pi@<pi-ip-address>

# Verbose output for debugging
ssh -v pi@<pi-ip-address>
```

#### **SSH Key Setup (Recommended)**
```bash
# Generate SSH key on your computer
ssh-keygen -t rsa -b 4096

# Copy key to Pi
ssh-copy-id pi@<pi-ip-address>

# Or manually copy key
cat ~/.ssh/id_rsa.pub | ssh pi@<pi-ip-address> 'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys'
```

#### **Performance Optimization**
The setup script applies these SSH optimizations for Pi Zero 2:
- **Compression enabled** for slower connections
- **DNS lookups disabled** for faster connection establishment
- **Keep-alive settings** to maintain stable connections
- **Optimized ciphers** for better performance on ARM hardware

#### **Security Notes**
- Default setup allows password authentication for initial setup
- Consider disabling password auth after setting up SSH keys:
  ```bash
  sudo nano /etc/ssh/sshd_config.d/99-pi-zero-2-fix.conf
  # Change: PasswordAuthentication no
  sudo systemctl restart ssh
  ```

## Development

### Local Testing

```bash
# Install dependencies
pip3 install -r requirements.txt

# Test the new display design
python3 test_new_design.py

# Start weather station
python3 weather_station.py
```

### Design Preview

To preview the new interface design without hardware:

```bash
# Generate preview images
python3 test_new_design.py

# View generated files:
# - weather_display_new_design.png (day mode)
# - weather_display_night_design.png (night mode)
```

### Code Structure

- `weather_station.py`: Main program and coordination
- `weather_api.py`: Open-Meteo API integration
- `display_manager.py`: E-Ink display control
- `config.py`: Configuration management

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Contributing

Contributions are welcome! Please create a pull request or open an issue.

## Acknowledgments

- [Open-Meteo](https://open-meteo.com/) for the free weather API
- [Waveshare](https://www.waveshare.com/) for the E-Ink display hardware
- Raspberry Pi Foundation for the amazing hardware platform
