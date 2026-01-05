#!/bin/bash
set -e

# Function to run sudo commands with password
run_sudo() {
    echo "max123" | sudo -S "$@"
}

echo "Updating system..."
run_sudo apt-get update

echo "Enabling I2C..."
run_sudo raspi-config nonint do_i2c 0

echo "Enabling Serial..."
run_sudo raspi-config nonint do_serial 0

echo "Installing system dependencies..."
run_sudo apt-get install -y python3-pip python3-venv

echo "Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo "Installing Python libraries..."
pip install pymodbus adafruit-circuitpython-ads1x15

echo "Setup complete."
