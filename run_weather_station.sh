#!/bin/bash

# Wrapper script to run weather station in virtual environment
# This handles the externally-managed-environment issue

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/weather_env"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# Install requirements if needed
if ! python -c "import requests, RPi.GPIO, spidev, PIL" 2>/dev/null; then
    echo "Installing Python packages in virtual environment..."
    pip install -r "$SCRIPT_DIR/requirements.txt"
fi

# Run the weather station
cd "$SCRIPT_DIR"
python weather_station.py
