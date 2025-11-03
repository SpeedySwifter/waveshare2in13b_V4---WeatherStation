#!/bin/bash

# Install Lato fonts for weather station
# Downloads Lato fonts from Google Fonts

echo "=== Installing Lato Fonts ==="
echo

# Create Lato directory
mkdir -p Lato

# Download Lato fonts from Google Fonts
echo "Downloading Lato fonts..."

# Check if we have curl or wget
if command -v curl &> /dev/null; then
    DOWNLOAD_CMD="curl -L -o"
elif command -v wget &> /dev/null; then
    DOWNLOAD_CMD="wget -O"
else
    echo "Error: Neither curl nor wget found. Please install one of them."
    exit 1
fi

# Google Fonts API URL for Lato
LATO_ZIP_URL="https://fonts.google.com/download?family=Lato"

# Download and extract Lato fonts
echo "Downloading Lato font family..."
$DOWNLOAD_CMD Lato.zip "$LATO_ZIP_URL"

if [ -f "Lato.zip" ]; then
    echo "Extracting fonts..."
    unzip -o Lato.zip -d Lato/
    rm Lato.zip
    
    # List installed fonts
    echo
    echo "✓ Lato fonts installed:"
    ls -la Lato/*.ttf 2>/dev/null || echo "No TTF files found in Lato directory"
    
    echo
    echo "=== Installation Complete! ==="
    echo "Lato fonts are now available in the Lato/ directory"
    echo "Test with: python3 test_new_design.py"
    
else
    echo "✗ Failed to download Lato fonts"
    echo
    echo "Manual installation:"
    echo "1. Visit https://fonts.google.com/specimen/Lato"
    echo "2. Download the font family"
    echo "3. Extract TTF files to the Lato/ directory"
    echo
    echo "Required files:"
    echo "  - Lato-Light.ttf"
    echo "  - Lato-Regular.ttf" 
    echo "  - Lato-Bold.ttf"
    echo "  - Lato-Black.ttf (optional)"
    exit 1
fi

echo
