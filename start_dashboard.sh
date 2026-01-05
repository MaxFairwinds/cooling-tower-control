#!/bin/bash
# Start web dashboard and expose via Tailscale Funnel

echo "Installing Flask..."
pip3 install flask --break-system-packages

echo ""
echo "Starting web dashboard on port 8000..."
python3 ~/web_dashboard.py &
WEB_PID=$!

sleep 3

echo ""
echo "Exposing via Tailscale Funnel..."
echo "This will generate a public HTTPS URL"
echo ""

sudo tailscale funnel 8000

# Cleanup on exit
trap "kill $WEB_PID" EXIT
