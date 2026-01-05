#!/bin/bash
# Installation script for Cooling Tower SCADA Backend
# Run on Raspberry Pi as root or with sudo

set -e  # Exit on error

echo "=========================================="
echo "Cooling Tower SCADA Backend Installation"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (sudo ./install.sh)"
    exit 1
fi

# 1. Install system dependencies
echo "Installing system packages..."
apt-get update
apt-get install -y \
    python3-pip \
    python3-venv \
    caddy \
    git \
    i2c-tools

# Enable I2C
echo "Enabling I2C..."
raspi-config nonint do_i2c 0

# 2. Create application directory
APP_DIR="/opt/cooling-tower"
echo "Creating application directory: $APP_DIR"
mkdir -p $APP_DIR
cd $APP_DIR

# 3. Create Python virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 4. Install Python dependencies
echo "Installing Python packages..."
pip install --upgrade pip
pip install -r /home/pi/insider_workspace/backend/requirements.txt

# Also need the existing dependencies
pip install pyserial adafruit-circuitpython-ads1x15

# 5. Copy backend files
echo "Copying backend files..."
cp -r /home/pi/insider_workspace/backend/* $APP_DIR/
cp /home/pi/insider_workspace/*.py $APP_DIR/  # Existing hardware modules

# 6. Install Caddy
echo "Configuring Caddy..."
cp $APP_DIR/Caddyfile /etc/caddy/Caddyfile
systemctl enable caddy
systemctl restart caddy

# 7. Create systemd service for FastAPI backend
echo "Creating systemd service..."
cat > /etc/systemd/system/cooling-tower.service << EOF
[Unit]
Description=Cooling Tower SCADA Backend
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=cooling-tower

[Install]
WantedBy=multi-user.target
EOF

# 8. Enable and start service
echo "Enabling service..."
systemctl daemon-reload
systemctl enable cooling-tower
systemctl start cooling-tower

# 9. Create React UI directory
echo "Creating React UI directory..."
mkdir -p /home/pi/cooling-tower-ui/dist
chown -R pi:pi /home/pi/cooling-tower-ui

# 10. Setup logging
echo "Setting up logging..."
mkdir -p /var/log/caddy
chown caddy:caddy /var/log/caddy

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Build React UI and copy to /home/pi/cooling-tower-ui/dist"
echo "2. Check backend status: sudo systemctl status cooling-tower"
echo "3. View logs: sudo journalctl -u cooling-tower -f"
echo "4. Check Caddy: sudo systemctl status caddy"
echo ""
echo "Access the UI at: http://$(hostname -I | awk '{print $1}')"
echo ""
