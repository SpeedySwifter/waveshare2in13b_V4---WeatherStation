#!/bin/bash

# Install SVG support for weather station icons
# This script installs Cairo library and cairosvg for SVG rendering

echo "=== Installing SVG Icon Support ==="
echo

# Detect operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "Detected macOS - Installing Cairo via Homebrew..."
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "Homebrew not found. Please install Homebrew first:"
        echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    
    # Install Cairo
    echo "Installing Cairo library..."
    brew install cairo
    
    # Install Python dependencies
    echo "Installing Python dependencies..."
    pip3 install cairosvg
    
elif [[ -f /proc/cpuinfo ]] && grep -q "Raspberry Pi\|BCM" /proc/cpuinfo; then
    # Raspberry Pi
    echo "Detected Raspberry Pi - Installing Cairo via apt..."
    
    # Update package list
    sudo apt update
    
    # Install Cairo development libraries
    echo "Installing Cairo development libraries..."
    sudo apt install -y libcairo2-dev libgirepository1.0-dev pkg-config python3-dev
    
    # Install Python dependencies
    echo "Installing Python dependencies..."
    pip3 install --break-system-packages cairosvg
    
else
    # Generic Linux
    echo "Detected Linux - Installing Cairo via package manager..."
    
    # Try different package managers
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y libcairo2-dev libgirepository1.0-dev pkg-config python3-dev
    elif command -v yum &> /dev/null; then
        sudo yum install -y cairo-devel gobject-introspection-devel pkgconfig python3-devel
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y cairo-devel gobject-introspection-devel pkgconfig python3-devel
    else
        echo "Unsupported package manager. Please install Cairo manually."
        exit 1
    fi
    
    # Install Python dependencies
    pip3 install cairosvg
fi

echo
echo "=== Installation Complete! ==="
echo
echo "SVG icon support should now be available."
echo "Test with: python3 test_new_design.py"
echo
echo "If you still get errors, the weather station will automatically"
echo "fall back to ASCII art icons, which also look great!"
echo
