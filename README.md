# Raspberry Pi Weather Station mit Waveshare 2.13" V4 E-Ink Display

Eine Wetterstation für den Raspberry Pi Zero 2 mit Waveshare 2.13" V4 E-Ink Display, die Wetterdaten über die OpenWeatherMap API abruft und anzeigt.

## Features

- **E-Ink Display**: Nutzt das Waveshare 2.13" V4 Display (schwarz/weiß)
- **Wetter API**: Ruft aktuelle Wetterdaten von OpenWeatherMap ab
- **Deutsche Sprache**: Unterstützt deutsche Wetterberichte
- **Energieeffizient**: E-Ink Display verbraucht nur beim Update Strom
- **Automatische Updates**: Konfigurierbare Update-Intervalle
- **Robuste Fehlerbehandlung**: Logging und Wiederherstellung bei Fehlern

## Hardware Anforderungen

- Raspberry Pi Zero 2 W
- Waveshare 2.13inch e-Paper HAT V4
- MicroSD Karte (16GB+)
- Stromversorgung (USB-C)

## Display Layout

Das 2.13" Display (250x122 Pixel) zeigt folgende Informationen:

- **Datum und Uhrzeit** (oben)
- **Stadtname**
- **Temperatur** (groß)
- **Wetterbeschreibung**
- **Luftfeuchtigkeit und Luftdruck**
- **Windgeschwindigkeit und -richtung**

## Quick Start

Für eine schnelle Installation verwende das automatische Setup-Script:

```bash
# Projekt klonen
git clone https://github.com/SpeedySwifter/waveshare2in13b_V4---WeatherStation.git weather-station
cd weather-station

# Automatisches Setup ausführen
bash setup.sh

# API Key in config.json eintragen
nano config.json

# System neustarten
sudo reboot
```

## Detaillierte Installation

### 1. Projekt klonen

```bash
cd ~
git clone https://github.com/SpeedySwifter/waveshare2in13b_V4---WeatherStation.git weather-station
cd weather-station
```

### 2. Automatisches Setup (empfohlen)

Das `setup.sh` Script installiert automatisch alle Abhängigkeiten:

```bash
bash setup.sh
```

Das Script führt folgende Schritte aus:
- System-Updates
- Installation aller Python-Abhängigkeiten
- SPI-Interface aktivieren
- Benutzer zu spi/gpio Gruppen hinzufügen
- Systemd Service installieren
- Beispiel-Konfiguration erstellen

### 3. Manuelle Installation

Falls du die Installation manuell durchführen möchtest:

```bash
# System aktualisieren
sudo apt update && sudo apt upgrade -y

# Abhängigkeiten installieren
sudo apt install -y python3 python3-pip python3-venv git python3-dev libjpeg-dev zlib1g-dev libfreetype-dev liblcms2-dev libopenjp2-7-dev libtiff-dev python3-pil python3-requests python3-rpi.gpio python3-spidev

# SPI aktivieren
sudo raspi-config
# Interface Options -> SPI -> Enable

# Benutzer zu Gruppen hinzufügen
sudo usermod -a -G spi,gpio $USER
```

### 4. OpenWeatherMap API Key

1. Registriere dich bei [OpenWeatherMap](https://openweathermap.org/api)
2. Erstelle einen kostenlosen API Key
3. Kopiere die Beispiel-Konfiguration:

```bash
cp config.json.example config.json
```

4. Bearbeite `config.json` und füge deinen API Key ein:

```json
{
    "api_key": "dein_api_key_hier",
    "city": "Berlin",
    "country_code": "DE",
    "update_interval": 30,
    "display_rotation": 0,
    "language": "de",
    "units": "metric"
}
```

### 5. Hardware Verbindung

Verbinde das Waveshare 2.13" V4 Display mit dem Raspberry Pi:

| Display Pin | Pi Pin | Funktion |
|-------------|--------|----------|
| VCC | 3.3V | Stromversorgung |
| GND | GND | Masse |
| DIN | GPIO 10 (MOSI) | SPI Data |
| CLK | GPIO 11 (SCLK) | SPI Clock |
| CS | GPIO 8 (CE0) | Chip Select |
| DC | GPIO 25 | Data/Command |
| RST | GPIO 17 | Reset |
| BUSY | GPIO 24 | Busy Signal |

## Verwendung

### Manueller Start

```bash
python3 weather_station.py
```

### Als Systemdienst (empfohlen)

Wenn du das `setup.sh` Script verwendet hast, ist der Service bereits installiert:

```bash
# Service starten
sudo systemctl start weather-station.service

# Status prüfen
sudo systemctl status weather-station.service
```

#### Manuelle Service Installation

Falls du den Service manuell installieren möchtest:

```bash
# Service-Datei kopieren
sudo cp weather-station.service /etc/systemd/system/

# Service aktivieren und starten
sudo systemctl daemon-reload
sudo systemctl enable weather-station.service
sudo systemctl start weather-station.service
```

## Konfiguration

### config.json Parameter

- **api_key**: OpenWeatherMap API Schlüssel
- **city**: Stadt für Wetterdaten (z.B. "Berlin", "München")
- **country_code**: Ländercode (z.B. "DE")
- **update_interval**: Update-Intervall in Minuten (Standard: 30)
- **display_rotation**: Display-Rotation in Grad (0, 90, 180, 270)
- **language**: Sprache für Wetterbeschreibungen ("de", "en")
- **units**: Einheiten ("metric" für Celsius, "imperial" für Fahrenheit)

### Umgebungsvariablen

Alternativ zum config.json kann der API Key als Umgebungsvariable gesetzt werden:

```bash
export OPENWEATHER_API_KEY="dein_api_key_hier"
```

## Zusätzliche Scripts

### setup.sh
Automatisches Setup-Script für die komplette Installation:
```bash
bash setup.sh
```

### install_autostart.sh
Installiert und konfiguriert den Autostart-Service:
```bash
bash install_autostart.sh
```

### health_check.sh
Überprüft den Status der Wetterstation und startet sie bei Bedarf neu:
```bash
bash health_check.sh
```

### run_weather_station.sh
Wrapper-Script zum Starten der Wetterstation:
```bash
bash run_weather_station.sh
```

## Projektstruktur

```
weather-station/
├── weather_station.py          # Hauptprogramm
├── weather_api.py             # OpenWeatherMap API Interface
├── display_manager.py         # E-Ink Display Management
├── config.py                  # Konfiguration laden
├── config.json.example        # Beispiel-Konfiguration
├── requirements.txt           # Python-Abhängigkeiten
├── weather-station.service    # Systemd Service
├── setup.sh                   # Automatisches Setup
├── install_autostart.sh       # Autostart Installation
├── health_check.sh           # Status-Überwachung
├── run_weather_station.sh    # Start-Script
├── waveshare_epd/            # Display-Treiber
└── README.md                 # Diese Datei
```

## Logs und Debugging

Logs werden in `weather_station.log` gespeichert:

```bash
# Live-Logs anzeigen
tail -f weather_station.log

# Service-Logs anzeigen
sudo journalctl -u weather-station.service -f
```

## Entwicklung und Testing

Für Entwicklung ohne Hardware:

```bash
# Erstellt PNG-Dateien statt E-Ink Display zu verwenden
python3 weather_station.py
```

Die generierten Bilder werden als `weather_display.png` gespeichert.

## Troubleshooting

### Display funktioniert nicht

1. SPI aktiviert? `sudo raspi-config`
2. Korrekte Verkabelung prüfen
3. Berechtigungen: `sudo usermod -a -G spi,gpio pi`

### API Fehler

1. API Key korrekt? Teste mit: `curl "http://api.openweathermap.org/data/2.5/weather?q=Berlin&appid=DEIN_API_KEY"`
2. Internetverbindung prüfen
3. API Limits erreicht? (1000 Aufrufe/Tag kostenlos)

### Service startet nicht

```bash
# Logs prüfen
sudo journalctl -u weather-station.service -n 50

# Manuell testen
cd /home/pi/weather-station
python3 weather_station.py
```

## Lizenz

MIT License - siehe LICENSE Datei für Details.

## Beiträge

Pull Requests und Issues sind willkommen! Bitte erstelle ein Issue bevor du größere Änderungen vornimmst.
