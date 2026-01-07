#!/bin/bash
# Start the data logger as a background service

cd /home/max/cooling-tower/backend

# Kill any existing logger
pkill -f data_logger.py

# Start new logger
nohup python3 data_logger.py > /tmp/data_logger.log 2>&1 &

echo "Data logger started"
echo "Log file: /var/log/cooling-tower/sensor_data.csv"
echo "Process log: /tmp/data_logger.log"

# Show status
sleep 2
pgrep -f data_logger.py && echo "✓ Logger is running" || echo "✗ Logger failed to start"
