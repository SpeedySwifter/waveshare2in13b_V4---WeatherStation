# Raspberry Pi Wetterstation mit Waveshare 2.13" V4 E-Ink Display

Eine Wetterstation für den Raspberry Pi Zero 2 mit Waveshare 2.13" V4 E-Ink Display, die Wetterdaten über die kostenlose Open-Meteo API abruft und anzeigt.

**🇺🇸 [English Version](README.md)**

## Features

- **E-Ink Display**: Nutzt das Waveshare 2.13" V4 Display (schwarz/weiß)
- **Wetter API**: Ruft aktuelle Wetterdaten von Open-Meteo ab (kostenlos, kein API-Key erforderlich)
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

## Schnellstart

Für eine schnelle Installation verwende das automatische Setup-Script:

```bash
# Projekt klonen
git clone https://github.com/SpeedySwifter/waveshare2in13b_V4---WeatherStation.git weather-station
cd weather-station

# Automatisches Setup ausführen
bash setup.sh

# Koordinaten in config.json anpassen (optional)
nano config.json

# System neustarten
sudo reboot
```

## Detaillierte Installation

### 1. Projekt klonen

```bash
git clone https://github.com/SpeedySwifter/waveshare2in13b_V4---WeatherStation.git weather-station
cd weather-station
```

### 2. Raspberry Pi OS vorbereiten

```bash
# System aktualisieren
sudo apt update && sudo apt upgrade -y

# Git installieren (falls nicht vorhanden)
sudo apt install -y git
```

### 3. Abhängigkeiten installieren

```bash
# Python und erforderliche Pakete installieren
sudo apt install -y python3 python3-pip python3-venv git python3-dev libjpeg-dev zlib1g-dev libfreetype-dev liblcms2-dev libopenjp2-7-dev libtiff-dev python3-pil python3-requests python3-rpi.gpio python3-spidev

# SPI aktivieren
sudo raspi-config
# Interface Options -> SPI -> Enable

# Benutzer zu Gruppen hinzufügen
sudo usermod -a -G spi,gpio $USER
```

### 4. Konfiguration

Kopiere die Beispiel-Konfiguration und passe sie an:

```bash
cp config.json.example config.json
```

Bearbeite `config.json` und passe die Koordinaten für deinen Standort an:

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

**Koordinaten finden:**
- Verwende [OpenStreetMap](https://www.openstreetmap.org/) oder Google Maps
- Klicke auf deinen gewünschten Standort
- Kopiere die Latitude (Breitengrad) und Longitude (Längengrad)

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

### Als Service installieren

```bash
# Service installieren
sudo cp weather-station.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable weather-station.service

# Service starten
sudo systemctl start weather-station.service

# Status prüfen
sudo systemctl status weather-station.service
```

### Service verwalten

```bash
# Service stoppen
sudo systemctl stop weather-station.service

# Service neustarten
sudo systemctl restart weather-station.service

# Service aktivieren und starten
sudo systemctl daemon-reload
sudo systemctl enable weather-station.service
sudo systemctl start weather-station.service
```

## Konfiguration

### config.json Parameter

- **latitude**: Breitengrad des Standorts (z.B. 54.3091)
- **longitude**: Längengrad des Standorts (z.B. 13.0818)
- **city**: Stadt für Anzeige (z.B. "Stralsund", "Berlin")
- **country_code**: Ländercode (z.B. "DE")
- **update_interval**: Update-Intervall in Minuten (Standard: 30)
- **display_rotation**: Display-Rotation in Grad (0, 90, 180, 270)
- **language**: Sprache für Wetterbeschreibungen ("de", "en")
- **units**: Einheiten ("metric" für Celsius, "imperial" für Fahrenheit)

## Zusätzliche Scripts

### setup.sh
Automatisches Setup-Script für die komplette Installation:
```bash
bash setup.sh
```

### health_check.sh
Überprüft den Status der Wetterstation und startet sie bei Bedarf neu:
```bash
bash health_check.sh
```

## Projektstruktur

```
weather-station/
├── weather_station.py          # Hauptprogramm
├── weather_api.py             # Open-Meteo API Interface
├── display_manager.py         # E-Ink Display Management
├── config.py                  # Konfiguration laden
├── config.json.example        # Beispiel-Konfiguration
├── requirements.txt           # Python-Abhängigkeiten
├── weather-station.service    # Systemd Service
├── setup.sh                   # Automatisches Setup
├── health_check.sh           # Status-Überwachung
├── waveshare_epd/            # Display-Treiber
├── README.md                 # Englische Dokumentation
├── README_DE.md              # Deutsche Dokumentation
└── .gitignore               # Git Ignore-Regeln
```

## Logs und Debugging

Logs werden in `weather_station.log` gespeichert:

```bash
# Live-Logs anzeigen
tail -f weather_station.log

# Service-Logs anzeigen
sudo journalctl -u weather-station.service -f

# Letzte Fehler anzeigen
sudo journalctl -u weather-station.service --since "1 hour ago"
```

### Häufige Probleme

1. **SPI nicht aktiviert**: `sudo raspi-config` → Interface Options → SPI → Enable
2. **Berechtigungsfehler**: Benutzer zu Gruppen hinzufügen: `sudo usermod -a -G spi,gpio $USER`
3. **Display zeigt nichts**: Hardware-Verbindungen prüfen
4. **Service startet nicht**: Logs prüfen: `sudo journalctl -u weather-station.service`

## Entwicklung

### Lokales Testen

```bash
# Abhängigkeiten installieren
pip3 install -r requirements.txt

# Wetterstation starten
python3 weather_station.py
```

### Code-Struktur

- `weather_station.py`: Hauptprogramm und Koordination
- `weather_api.py`: Open-Meteo API Integration
- `display_manager.py`: E-Ink Display Steuerung
- `config.py`: Konfigurationsverwaltung

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe LICENSE-Datei für Details.

## Beiträge

Beiträge sind willkommen! Bitte erstelle einen Pull Request oder öffne ein Issue.

## Danksagungen

- [Open-Meteo](https://open-meteo.com/) für die kostenlose Wetter-API
- [Waveshare](https://www.waveshare.com/) für die E-Ink Display Hardware
- Raspberry Pi Foundation für die großartige Hardware-Plattform
