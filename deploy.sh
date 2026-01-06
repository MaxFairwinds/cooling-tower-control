#!/bin/bash
# Deploy Cooling Tower SCADA to Raspberry Pi

set -e  # Exit on error

# Configuration
PI_USER="max"
PI_HOST="100.89.57.3"
PI_BACKEND_DIR="/home/max/cooling-tower/backend"
PI_FRONTEND_DIR="/home/max/cooling-tower/frontend"

echo "========================================="
echo "Deploying Cooling Tower SCADA System"
echo "========================================="

# Check if Pi is reachable
echo "Checking Pi connectivity..."
if ! ping -c 1 "$PI_HOST" &> /dev/null; then
    echo "Error: Cannot reach $PI_HOST"
    echo "Make sure the Raspberry Pi is on and connected to the network"
    exit 1
fi

echo "✓ Pi is reachable"

# Create directories on Pi
echo "Creating directories on Pi..."
ssh "$PI_USER@$PI_HOST" "mkdir -p $PI_BACKEND_DIR $PI_FRONTEND_DIR"

# Deploy backend
echo "Deploying backend..."
rsync -avz --exclude='__pycache__' --exclude='*.pyc' --exclude='.git' \
    backend/ "$PI_USER@$PI_HOST:$PI_BACKEND_DIR/"

# Copy core modules (they're imported from parent dir)
echo "Deploying core modules..."
scp config.py vfd_controller.py sensor_manager.py pump_failover.py main_control.py \
    "$PI_USER@$PI_HOST:$PI_BACKEND_DIR/" 2>/dev/null || echo "Modules already in backend/"

# Deploy frontend build
echo "Deploying frontend..."
rsync -avz --delete frontend/dist/ "$PI_USER@$PI_HOST:$PI_FRONTEND_DIR/dist/"

# Install backend dependencies
echo "Setting up Python virtual environment and installing dependencies..."
ssh "$PI_USER@$PI_HOST" "cd $PI_BACKEND_DIR && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"

# Make install script executable
ssh "$PI_USER@$PI_HOST" "chmod +x $PI_BACKEND_DIR/install.sh"

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. SSH to Pi: ssh $PI_USER@$PI_HOST"
echo "2. Run backend installer: cd $PI_BACKEND_DIR && sudo ./install.sh"
echo "3. Start backend: sudo systemctl start cooling-tower"
echo "4. Check status: sudo systemctl status cooling-tower"
echo "5. View logs: sudo journalctl -u cooling-tower -f"
echo ""
echo "Access UI at: http://$PI_HOST/"
echo ""
