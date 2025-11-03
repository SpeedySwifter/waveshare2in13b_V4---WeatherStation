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

- Raspberry Pi Zero 2 W
- Waveshare 2.13inch e-Paper HAT V4
- MicroSD Card (16GB+)
- Power Supply (USB-C)

## Display Layout

The 2.13" display (250x122 pixels) shows the following information:

- **Date and Time** (top)
- **City Name**
- **Temperature** (large)
- **Weather Description**
- **Humidity and Pressure**
- **Wind Speed and Direction**

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
├── display_manager.py         # E-Ink display management
├── config.py                  # Configuration loader
├── config.json.example        # Example configuration
├── requirements.txt           # Python dependencies
├── weather-station.service    # Systemd service
├── setup.sh                   # Automatic setup
├── health_check.sh           # Status monitoring
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

## Development

### Local Testing

```bash
# Install dependencies
pip3 install -r requirements.txt

# Start weather station
python3 weather_station.py
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
