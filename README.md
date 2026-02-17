# 🌦️ Raspberry Pi E-Ink Weather Station

> Real-time weather display on energy-efficient e-paper with Waveshare 2.13" V4 display and Raspberry Pi Zero 2

Beautiful, minimalist weather station that shows current conditions, forecast, and detailed metrics on a crisp black-and-white e-ink display. Perfect for your desk, smart home, or as a learning project for embedded systems.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-Zero%202%20W-red.svg)](https://www.raspberrypi.com/)
[![E-Ink Display](https://img.shields.io/badge/Display-Waveshare%202.13%22%20V4-black.svg)](https://www.waveshare.com/)
[![API](https://img.shields.io/badge/API-Open--Meteo-green.svg)](https://open-meteo.com/)
[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

🇩🇪 **[Deutsche Version / German Version](README_DE.md)**

---

## 📸 Display Preview

```
╔══════════════════════════════════════════════════╗
║  📅 Montag, 17. Februar        🕐 14:30 Uhr      ║
╠══════════════════════════════════════════════════╣
║                                                  ║
║              🌤️  Stralsund                      ║
║              ────────────                        ║
║                                                  ║
║                   15°C                           ║
║                                                  ║
║              Teilweise bewölkt                   ║
║                                                  ║
║  ╭────────────────────────────────────────────╮  ║
║  │  💧 Luftfeuchtigkeit: 65%                 │  ║
║  │  📊 Luftdruck: 1013 hPa                   │  ║
║  │  💨 Windgeschwindigkeit: 3.5 m/s          │  ║
║  │  🧭 Windrichtung: 245°                    │  ║
║  ╰────────────────────────────────────────────╯  ║
╚══════════════════════════════════════════════════╝
```

---

## ✨ Features

### 🎨 **Modern Display Design**
- **Professional typography** – Merriweather Sans font family with 5 weight variations
- **High-quality PNG icons** – Day/night weather variations with ASCII art fallback
- **Clean layout** – Header bar, decorative elements, bordered panels
- **E-ink optimized** – Perfect contrast for black/white displays

### 🌍 **Weather Data**
- **Real-time updates** – Live data from Open-Meteo API (free, no key required!)
- **Comprehensive metrics** – Temperature, humidity, pressure, wind speed/direction
- **German language** – Full localization support
- **Custom locations** – GPS coordinates for anywhere in the world

### ⚡ **Energy Efficiency**
- **E-ink technology** – Display only uses power during updates
- **Configurable intervals** – Update every 30 minutes or customize
- **Low power consumption** – Perfect for always-on display

### 🔧 **Smart Features**
- **Automatic service** – Runs as systemd background service
- **Error recovery** – Robust error handling and logging
- **Health monitoring** – Status checks and auto-restart
- **One-click setup** – Automated installation script

---

## 🛠️ Hardware Requirements

| Component | Specification | Link |
|-----------|---------------|------|
| **Microcontroller** | Raspberry Pi Zero 2 W | [Buy](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/) |
| **Display** | Waveshare 2.13" e-Paper HAT V4 (B/W) | [Buy](https://www.waveshare.com/2.13inch-e-paper-hat.htm) |
| **Storage** | MicroSD Card (16GB+, Class 10) | - |
| **Power** | Micro-USB Power Supply (5V/2.5A) | - |
| **Connectivity** | Wi-Fi (built-in on Pi Zero 2 W) | - |

**Total Cost:** ~$40-50 USD

---

## 🔌 Hardware Connection

### Pin Mapping

| Display Pin | Raspberry Pi Pin | BCM GPIO | Function |
|-------------|------------------|----------|----------|
| VCC | Pin 1 | - | 3.3V Power |
| GND | Pin 6 | - | Ground |
| DIN | Pin 19 | GPIO 10 | SPI MOSI |
| CLK | Pin 23 | GPIO 11 | SPI SCLK |
| CS | Pin 24 | GPIO 8 | SPI CE0 |
| DC | Pin 22 | GPIO 25 | Data/Command |
| RST | Pin 11 | GPIO 17 | Reset |
| BUSY | Pin 18 | GPIO 24 | Busy Signal |

### Wiring Diagram

```
Raspberry Pi Zero 2 W          Waveshare 2.13" V4
    ┌─────────┐                   ┌──────────┐
    │  3.3V   ├───────────────────┤ VCC      │
    │  GND    ├───────────────────┤ GND      │
    │  GPIO10 ├───────────────────┤ DIN      │
    │  GPIO11 ├───────────────────┤ CLK      │
    │  GPIO8  ├───────────────────┤ CS       │
    │  GPIO25 ├───────────────────┤ DC       │
    │  GPIO17 ├───────────────────┤ RST      │
    │  GPIO24 ├───────────────────┤ BUSY     │
    └─────────┘                   └──────────┘
```

---

## 🚀 Quick Start

### One-Command Installation

```bash
# Clone and setup in one go
git clone https://github.com/SpeedySwifter/waveshare2in13b_V4---WeatherStation.git weather-station && \
cd weather-station && \
bash setup.sh
```

The setup script will:
- ✅ Update system packages
- ✅ Install Python dependencies
- ✅ Enable SPI interface
- ✅ Configure user permissions
- ✅ Install Merriweather Sans fonts
- ✅ Setup systemd service
- ✅ Configure SSH (optimized for Pi Zero 2)
- ✅ Create config file

After setup:
```bash
# Edit your location
nano config.json

# Reboot
sudo reboot
```

Done! ✨ Your weather station will start automatically on boot.

---

## ⚙️ Manual Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/SpeedySwifter/waveshare2in13b_V4---WeatherStation.git weather-station
cd weather-station
```

### 2️⃣ System Preparation

```bash
# Update Raspberry Pi OS
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y \
  python3 python3-pip python3-venv \
  python3-dev libjpeg-dev zlib1g-dev \
  libfreetype-dev liblcms2-dev \
  libopenjp2-7-dev libtiff-dev \
  python3-pil python3-requests \
  python3-rpi.gpio python3-spidev \
  git fonts-liberation

# Enable SPI interface
sudo raspi-config
# Navigate to: Interface Options → SPI → Enable
```

### 3️⃣ Python Dependencies

```bash
# Install Python packages
pip3 install -r requirements.txt
```

### 4️⃣ Configure Location

```bash
# Copy example config
cp config.json.example config.json

# Edit with your coordinates
nano config.json
```

**Find Your Coordinates:**
- Visit [OpenStreetMap](https://www.openstreetmap.org/)
- Search for your location
- Right-click → "Show coordinates"
- Copy Latitude and Longitude

**Example Configuration:**
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

### 5️⃣ Install as Service

```bash
# Install and enable service
sudo bash install_service.sh

# Start service
sudo systemctl start weather-station.service

# Check status
sudo systemctl status weather-station.service
```

---

## 📁 Project Structure

```
weather-station/
├── .github/                      # GitHub configuration
├── fonts/                        # Font files
├── icons png/                    # PNG weather icons
├── Merriweather_Sans/            # Professional font family
├── waveshare_epd/               # E-ink display drivers
├── weather_station.py           # Main application
├── weather_api.py               # Open-Meteo API client
├── display_manager.py           # Display rendering (modern design)
├── display_manager_enhanced.py  # Enhanced display features
├── config.py                    # Configuration loader
├── config.json.example          # Example configuration
├── requirements.txt             # Python dependencies
├── weather-station.service      # Systemd service file
├── setup.sh                     # Automated setup script
├── install_service.sh           # Service installation
├── install_lato_fonts.sh        # Font installation
├── install_svg_support.sh       # SVG support (legacy)
├── download_weather_icons.sh    # Icon downloader
├── health_check.sh              # Health monitoring
├── ssh_fix.sh                   # SSH optimization for Pi Zero 2
├── test_new_design.py          # Design preview generator
├── README.md                    # English documentation (this file)
├── README_DE.md                 # German documentation
└── .gitignore                   # Git ignore rules
```

---

## ⚠️ Known Issues

### 🐛 Icon Display Bug

**Status:** Currently being investigated

**Issue:** Weather icons may not display correctly or appear in wrong positions on the e-ink display.

**Temporary Workaround:**
- The system falls back to ASCII art weather symbols
- All other functionality (temperature, humidity, etc.) works correctly
- Weather descriptions remain accurate

**Tracking:** [GitHub Issue](https://github.com/SpeedySwifter/waveshare2in13b_V4---WeatherStation/issues)

**Updates:** Fix is in progress - check the repository for latest updates

---

## 📖 Configuration Options

### config.json Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `latitude` | float | - | Your location's latitude (e.g., 54.3091) |
| `longitude` | float | - | Your location's longitude (e.g., 13.0818) |
| `city` | string | - | City name for display (e.g., "Stralsund") |
| `country_code` | string | "DE" | ISO country code |
| `update_interval` | int | 30 | Update interval in minutes |
| `display_rotation` | int | 0 | Display rotation (0, 90, 180, 270) |
| `language` | string | "de" | Language code ("de", "en") |
| `units` | string | "metric" | Unit system ("metric", "imperial") |

### Example Configurations

**Berlin, Germany:**
```json
{
    "latitude": 52.5200,
    "longitude": 13.4050,
    "city": "Berlin",
    "country_code": "DE",
    "update_interval": 30,
    "display_rotation": 0,
    "language": "de",
    "units": "metric"
}
```

**London, UK:**
```json
{
    "latitude": 51.5074,
    "longitude": -0.1278,
    "city": "London",
    "country_code": "GB",
    "update_interval": 30,
    "display_rotation": 0,
    "language": "en",
    "units": "metric"
}
```

**New York, USA:**
```json
{
    "latitude": 40.7128,
    "longitude": -74.0060,
    "city": "New York",
    "country_code": "US",
    "update_interval": 30,
    "display_rotation": 0,
    "language": "en",
    "units": "imperial"
}
```

---

## 🎯 Usage

### Service Management

```bash
# Start weather station
sudo systemctl start weather-station.service

# Stop weather station
sudo systemctl stop weather-station.service

# Restart weather station
sudo systemctl restart weather-station.service

# Check status
sudo systemctl status weather-station.service

# Enable auto-start on boot
sudo systemctl enable weather-station.service

# Disable auto-start
sudo systemctl disable weather-station.service
```

### Manual Execution

```bash
# Run once (foreground)
python3 weather_station.py

# Run with debug output
python3 weather_station.py --debug

# Test display without API call
python3 test_new_design.py
```

### View Logs

```bash
# Real-time logs
tail -f weather_station.log

# Service logs
sudo journalctl -u weather-station.service -f

# Last 100 lines
sudo journalctl -u weather-station.service -n 100

# Logs from last hour
sudo journalctl -u weather-station.service --since "1 hour ago"

# Logs with errors only
sudo journalctl -u weather-station.service -p err
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Display shows nothing

**Symptoms:** Blank e-ink display

**Solutions:**
```bash
# Check SPI is enabled
lsmod | grep spi

# If not, enable it
sudo raspi-config
# Interface Options → SPI → Enable

# Verify connections
# Check all pins are properly connected

# Test display
python3 test_new_design.py
```

#### 2. SPI Permission Denied

**Symptoms:** `Permission denied: '/dev/spidev0.0'`

**Solution:**
```bash
# Add user to SPI group
sudo usermod -a -G spi,gpio $USER

# Logout and login again, or reboot
sudo reboot
```

#### 3. Weather API Error

**Symptoms:** No weather data displayed

**Solutions:**
```bash
# Check internet connection
ping -c 4 open-meteo.com

# Verify coordinates in config.json
nano config.json

# Test API manually
curl "https://api.open-meteo.com/v1/forecast?latitude=54.3091&longitude=13.0818&current_weather=true"

# Check logs
tail -f weather_station.log
```

#### 4. Service won't start

**Symptoms:** `systemctl status` shows failed

**Solutions:**
```bash
# Check detailed error
sudo journalctl -u weather-station.service -n 50

# Verify Python dependencies
pip3 install -r requirements.txt

# Check file permissions
ls -la weather_station.py

# Make executable if needed
chmod +x weather_station.py

# Reload service
sudo systemctl daemon-reload
sudo systemctl restart weather-station.service
```

#### 5. Font issues

**Symptoms:** Strange characters or missing text

**Solution:**
```bash
# Reinstall fonts
bash install_lato_fonts.sh

# Or manually
sudo apt install fonts-liberation fonts-dejavu-core

# Clear font cache
fc-cache -f -v
```

#### 6. Icons not displaying (Known Bug)

**Symptoms:** Weather icons missing or incorrectly positioned

**Current Status:** Bug is being investigated

**Workaround:**
- ASCII art symbols are used as fallback
- All weather data still displays correctly

---

## 🧪 Development & Testing

### Local Testing

```bash
# Install development dependencies
pip3 install -r requirements.txt

# Generate display preview (no hardware needed)
python3 test_new_design.py

# View generated previews
ls -lh weather_display_*.png
```

### Preview Output Files

The `test_new_design.py` script generates:
- `weather_display_new_design.png` – Day mode preview
- `weather_display_night_design.png` – Night mode preview

### Code Structure

```python
# Main application flow
weather_station.py
├── config.py              # Load configuration
├── weather_api.py         # Fetch weather data
└── display_manager.py     # Render to e-ink

# Weather API client
weather_api.py
├── fetch_weather()        # Get current conditions
├── fetch_forecast()       # Get forecast data
└── parse_response()       # Parse API response

# Display management
display_manager.py
├── init_display()         # Initialize e-ink
├── render_weather()       # Draw weather UI
├── draw_header()          # Date/time bar
├── draw_weather_info()    # Main weather display
└── draw_details()         # Humidity, pressure, wind
```

### Adding Custom Features

**Example: Add UV Index**

1. Modify API request in `weather_api.py`:
```python
params = {
    'current_weather': True,
    'hourly': 'uv_index'  # Add UV index
}
```

2. Update display in `display_manager.py`:
```python
# Add UV index display
draw.text((x, y), f"☀️ UV Index: {uv_index}", font=font)
```

---

## 📊 Performance & Stats

| Metric | Value |
|--------|-------|
| **Display Resolution** | 250x122 pixels |
| **Update Time** | ~3-5 seconds |
| **Power Consumption** | < 0.5W average |
| **API Calls** | 1 per update interval |
| **Memory Usage** | ~50MB RAM |
| **Storage** | ~200MB (with dependencies) |
| **Boot Time** | ~30 seconds to first update |

---

## 🔐 Privacy & Security

- ✅ **No data collection** – All data stays on your device
- ✅ **No API keys required** – Open-Meteo is completely free
- ✅ **Local processing** – Weather data processed on Pi
- ✅ **No cloud services** – Fully self-contained
- ✅ **Open source** – Full code transparency

**What data is accessed:**
- ✅ Weather data from Open-Meteo API (public, anonymous)
- ✅ Your GPS coordinates (only sent to weather API)

**What is NOT accessed:**
- ❌ No personal data collection
- ❌ No usage tracking
- ❌ No third-party analytics

---

## 🛣️ Roadmap

### Planned Features
- [ ] **Fix icon display bug** (in progress)
- [ ] **Multi-day forecast** – Show 5-day weather forecast
- [ ] **Custom themes** – Different display layouts
- [ ] **Weather alerts** – Severe weather notifications
- [ ] **Historical data** – Temperature graphs
- [ ] **Multiple locations** – Cycle through cities
- [ ] **Astronomical data** – Sunrise/sunset times
- [ ] **Air quality** – PM2.5, AQI display
- [ ] **Web interface** – Remote configuration
- [ ] **REST API** – Query weather data remotely

### Future Hardware Support
- [ ] Larger e-ink displays (4.2", 7.5")
- [ ] Color e-ink displays
- [ ] Waveshare V3 compatibility
- [ ] Button controls for manual refresh

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Reporting Bugs

1. Check [existing issues](https://github.com/SpeedySwifter/waveshare2in13b_V4---WeatherStation/issues)
2. Create a new issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - System info (Pi model, OS version)
   - Logs (`weather_station.log`)

### Submitting Code

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Add comments for complex logic
- Update documentation
- Test on actual hardware when possible
- Include preview images for UI changes

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**TL;DR:** Free to use, modify, and distribute. Just include the original license.

---

## 🙏 Acknowledgments

- **[Open-Meteo](https://open-meteo.com/)** – Free weather API with no key required
- **[Waveshare](https://www.waveshare.com/)** – High-quality e-ink display hardware
- **[Raspberry Pi Foundation](https://www.raspberrypi.com/)** – Amazing single-board computers
- **[Python Imaging Library (Pillow)](https://python-pillow.org/)** – Image processing
- **Merriweather Sans** – Beautiful typography

---

## 💬 Support & Community

- 🐛 **Bug Reports:** [GitHub Issues](https://github.com/SpeedySwifter/waveshare2in13b_V4---WeatherStation/issues)
- 💡 **Feature Requests:** [GitHub Discussions](https://github.com/SpeedySwifter/waveshare2in13b_V4---WeatherStation/discussions)
- 📧 **Email:** sven@hajer.dev
- 🌐 **Website:** [hajer.dev](https://hajer.dev)
- 📚 **Documentation:** [Wiki](https://github.com/SpeedySwifter/waveshare2in13b_V4---WeatherStation/wiki)

---

## 🌟 Related Projects

Check out these other awesome projects:

- **[ESP32 MacBook Monitor](https://github.com/SpeedySwifter/esp32_macbook_system_resources)** – System stats on ESP32 display
- **[Daily Spotify Playlists](https://github.com/SpeedySwifter/Daily-Playlist-Generator-for-Spotify)** – Auto-generated daily playlists
- **[AVR Gaming](https://github.com/SpeedySwifter/avr-gaming)** – eSport organization website

---

## 👤 Author

**Sven Hajer**  
Freelance Full-Stack Developer & Hardware Enthusiast

- GitHub: [@SpeedySwifter](https://github.com/SpeedySwifter)
- Website: [hajer.dev](https://hajer.dev)
- Email: sven@hajer.dev

---

<div align="center">

**Made with ❤️ and ☕ for the maker community**

[![Stars](https://img.shields.io/github/stars/SpeedySwifter/waveshare2in13b_V4---WeatherStation?style=social)](https://github.com/SpeedySwifter/waveshare2in13b_V4---WeatherStation/stargazers)
[![Forks](https://img.shields.io/github/forks/SpeedySwifter/waveshare2in13b_V4---WeatherStation?style=social)](https://github.com/SpeedySwifter/waveshare2in13b_V4---WeatherStation/network/members)

**If you found this project helpful, consider giving it a ⭐**

---

### 📸 Show Your Build!

Built your own weather station? Share it!
- Tweet with #RaspberryPiWeather
- Open a discussion with photos
- Submit to [Awesome Raspberry Pi Projects](https://github.com/thibmaek/awesome-raspberry-pi)

---

*Stay updated with the weather, the maker way!* 🌤️

</div
