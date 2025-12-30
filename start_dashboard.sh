#!/bin/bash

# Auto-detect USB serial device and update config
python3 << 'PYCODE'
import glob

devices = sorted(glob.glob('/dev/ttyUSB*') + glob.glob('/dev/ttyACM*'))
if devices:
    device = devices[0]
    print(f'Detected USB device: {device}')
    
    with open('/home/max/config.py', 'r') as f:
        config = f.read()
    
    lines = config.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('SERIAL_PORT ='):
            lines[i] = f"SERIAL_PORT = '{device}'  # USB-RS485 adapter (auto-detected)"
            break
    
    with open('/home/max/config.py', 'w') as f:
        f.write('\n'.join(lines))
    print('Updated config.py')
else:
    print('WARNING: No USB serial device found!')
PYCODE

# Kill existing dashboard
pkill -f web_dashboard.py

# Start dashboard in background
echo 'Starting web dashboard on port 8000...'
python3 ~/web_dashboard.py > ~/dashboard.log 2>&1 &

# Wait for it to start
sleep 3

# Enable Tailscale Funnel (run in background)
nohup sudo tailscale funnel 8000 > /dev/null 2>&1 &

sleep 1
echo ''
echo 'Dashboard started!'
echo "Local: http://:8000"
echo 'Public: https://coolingtower.tailc1d288.ts.net/'
