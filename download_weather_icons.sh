#!/bin/bash

# Create fonts directory if it doesn't exist
mkdir -p fonts

# Download Weather Icons font
curl -L -o fonts/weathericons-regular-webfont.ttf 'https://github.com/erikflowers/weather-icons/raw/2.0.10/font/weathericons-regular-webfont.ttf'

# Download Lato font (clean, modern font for text)
curl -L -o fonts/Lato-Regular.ttf 'https://github.com/google/fonts/raw/main/ofl/lato/Lato-Regular.ttf'
curl -L -o fonts/Lato-Bold.ttf 'https://github.com/google/fonts/raw/main/ofl/lato/Lato-Bold.ttf'

echo "Fonts downloaded to fonts/ directory"
