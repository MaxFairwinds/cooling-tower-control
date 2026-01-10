#!/bin/bash
# Deploy Cooling Tower SCADA to Raspberry Pi

set -e  # Exit on error

# Configuration
PI_USER="max"
PI_HOST="100.89.57.3"
BACKEND_SOURCE_DIR="/home/max"  # Where Flask imports from
OLD_DASHBOARD_DIR="/home/max/old_dashboard"

# Digital Ocean droplet for React frontend
DO_HOST="phytocontrol"  # SSH alias for 159.89.150.146
DO_FRONTEND_DIR="/var/www/cooling-tower"

echo "========================================="
echo "Deploying Cooling Tower SCADA System"
echo "========================================="

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  WARNING: You have uncommitted changes"
    git status --short
    echo ""
fi

# Check if Pi is reachable
echo "Checking Pi connectivity..."
if ! ping -c 1 "$PI_HOST" &> /dev/null; then
    echo "Error: Cannot reach $PI_HOST"
    echo "Make sure the Raspberry Pi is on and connected to the network"
    exit 1
fi

echo "✓ Pi is reachable"

# Deploy core modules to /home/max (Flask imports from here)
echo "Deploying core modules to $BACKEND_SOURCE_DIR..."
ssh "$PI_USER@$PI_HOST" "mkdir -p $BACKEND_SOURCE_DIR"
scp backend/{vfd_controller,sensor_manager,pump_failover,config,serial_lock}.py \
    "$PI_USER@$PI_HOST:$BACKEND_SOURCE_DIR/"

# Deploy Flask dashboard
echo "Deploying Flask dashboard..."
ssh "$PI_USER@$PI_HOST" "mkdir -p $OLD_DASHBOARD_DIR/templates"
scp old_dashboard/web_dashboard.py "$PI_USER@$PI_HOST:$OLD_DASHBOARD_DIR/"
scp old_dashboard/templates/dashboard.html "$PI_USER@$PI_HOST:$OLD_DASHBOARD_DIR/templates/"

# Deploy login template if it exists
if [ -f "old_dashboard/templates/login.html" ]; then
    scp old_dashboard/templates/login.html "$PI_USER@$PI_HOST:$OLD_DASHBOARD_DIR/templates/"
fi

# Restart Flask (if running)
echo "Restarting Flask dashboard..."
ssh "$PI_USER@$PI_HOST" "pkill -f web_dashboard || true; sleep 2; cd $OLD_DASHBOARD_DIR && nohup python3 web_dashboard.py > /tmp/flask.log 2>&1 &"
echo "Waiting for Flask to start..."
sleep 3

# Restart FastAPI (if running)
echo "Restarting FastAPI proxy..."
ssh "$PI_USER@$PI_HOST" "pkill -f 'uvicorn.*main_proxy' || true; sleep 2; cd /home/max/cooling-tower/backend && nohup python3 -m uvicorn main_proxy:app --host 0.0.0.0 --port 8000 > /tmp/fastapi.log 2>&1 &"
echo "Waiting for FastAPI to start..."
sleep 2

# Deploy React frontend to Digital Ocean droplet
echo ""
echo "Building and deploying React frontend to DO droplet..."
cd frontend
npm run build
rsync -avz --delete dist/ "$DO_HOST:$DO_FRONTEND_DIR/"
ssh "$DO_HOST" "chown -R caddy:caddy $DO_FRONTEND_DIR"
cd ..

echo ""
echo "========================================="
echo "Deployment Complete!"
echo "========================================="
echo ""
echo "Services running on Pi:"
echo "  Flask:   http://100.89.57.3:8001"
echo "  FastAPI: http://100.89.57.3:8000"
echo ""
echo "Public access:"
echo "  React UI:    http://159.89.150.146"
echo "  Flask UI:    http://159.89.150.146:8001"
echo ""
echo "Check logs:"
echo "  Flask:   ssh $PI_USER@$PI_HOST 'tail -f /tmp/flask.log'"
echo "  FastAPI: ssh $PI_USER@$PI_HOST 'tail -f /tmp/fastapi.log'"
echo ""
