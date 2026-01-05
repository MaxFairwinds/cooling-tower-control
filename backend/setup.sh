#!/bin/bash
# Setup script for Cooling Tower Control System on Raspberry Pi

echo "=========================================="
echo "Cooling Tower Control System Setup"
echo "=========================================="

# Enable I2C
echo ""
echo "Checking I2C..."
if ! grep -q "^dtparam=i2c_arm=on" /boot/config.txt; then
    echo "Enabling I2C interface..."
    sudo raspi-config nonint do_i2c 0
    echo "I2C enabled (reboot required)"
else
    echo "I2C already enabled"
fi

# Install required Python packages
echo ""
echo "Installing Python dependencies..."
sudo pip3 install pyserial adafruit-circuitpython-ads1x15 --break-system-packages

# Check for ADS1115
echo ""
echo "Checking for ADS1115 on I2C bus..."
if command -v i2cdetect &> /dev/null; then
    echo "I2C devices:"
    sudo i2cdetect -y 1
else
    echo "i2c-tools not installed, installing..."
    sudo apt-get update
    sudo apt-get install -y i2c-tools
    echo "I2C devices:"
    sudo i2cdetect -y 1
fi

# Check for USB-RS485 adapter
echo ""
echo "Checking for USB-RS485 adapter..."
if [ -e /dev/ttyUSB0 ]; then
    echo "✓ Found /dev/ttyUSB0"
    ls -la /dev/ttyUSB0
else
    echo "⚠ /dev/ttyUSB0 not found - plug in USB-RS485 adapter"
fi

# Set permissions
echo ""
echo "Setting file permissions..."
chmod +x main_control.py

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Connect ADS1115 to I2C pins (GPIO 2/3)"
echo "2. Connect pressure sensor to ADS1115 A0"
echo "3. Connect temperature sensor to ADS1115 A1"
echo "4. Connect USB-RS485 adapter"
echo "5. Wire RS485 A-A, B-B, GND-GND to VFDs"
echo "6. Scan for VFDs: python3 g540_scanner.py"
echo "7. Update config.py with correct device IDs"
echo "8. Run: python3 main_control.py"
echo ""
