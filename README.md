# Raspberry Pi Weather Station mit Waveshare 2.13" B V4 E-Ink Display

Eine Wetterstation für den Raspberry Pi Zero 2 mit Waveshare 2.13" B V4 E-Ink Display, die Wetterdaten über die OpenWeatherMap API abruft und anzeigt.

## Features

- **E-Ink Display**: Nutzt das Waveshare 2.13" B V4 Display (schwarz/rot/weiß)
- **Wetter API**: Ruft aktuelle Wetterdaten von OpenWeatherMap ab
- **Deutsche Sprache**: Unterstützt deutsche Wetterberichte
- **Energieeffizient**: E-Ink Display verbraucht nur beim Update Strom
- **Automatische Updates**: Konfigurierbare Update-Intervalle
- **Robuste Fehlerbehandlung**: Logging und Wiederherstellung bei Fehlern

## Hardware Anforderungen

- Raspberry Pi Zero 2 W
- Waveshare 2.13inch e-Paper HAT (B) V4
- MicroSD Karte (16GB+)
- Stromversorgung (USB-C)

## Display Layout

Das 2.13" Display (250x122 Pixel) zeigt folgende Informationen:

- **Datum und Uhrzeit** (oben)
- **Stadtname**
- **Temperatur** (groß, in rot)
- **Wetterbeschreibung**
- **Luftfeuchtigkeit und Luftdruck**
- **Windgeschwindigkeit und -richtung**

## Installation

### 1. Raspberry Pi OS Setup

```bash
# System aktualisieren
sudo apt update && sudo apt upgrade -y

# Python und Git installieren
sudo apt install python3 python3-pip git -y

# SPI aktivieren
sudo raspi-config
# Interface Options -> SPI -> Enable
```

### 2. Projekt klonen

```bash
cd ~
git clone <repository-url> weather-station
cd weather-station
```

### 3. Python Dependencies installieren

```bash
pip3 install -r requirements.txt
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

Verbinde das Waveshare 2.13" B V4 Display mit dem Raspberry Pi:

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

1. Erstelle eine Systemd Service Datei:

```bash
sudo nano /etc/systemd/system/weather-station.service
```

2. Füge folgenden Inhalt ein:

```ini
[Unit]
Description=Weather Station
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/weather-station
ExecStart=/usr/bin/python3 /home/pi/weather-station/weather_station.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Service aktivieren und starten:

```bash
sudo systemctl daemon-reload
sudo systemctl enable weather-station.service
sudo systemctl start weather-station.service
```

4. Status prüfen:

```bash
sudo systemctl status weather-station.service
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

Die generierten Bilder werden als `weather_display_black.png` und `weather_display_red.png` gespeichert.

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
