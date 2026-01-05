# Cooling Tower SCADA - FastAPI Backend

Modern real-time backend for cooling tower monitoring and control.

## Features

- **Real-time WebSocket** - Live data streaming to UI (500ms updates)
- **REST API** - Full control endpoints for pumps, fan, settings
- **Fan Auto Control** - PID with hysteresis (75°F ±5°F deadband)
- **Weather Integration** - Weather.gov API for outdoor conditions
- **Modbus RTU** - 3x GALT G540 VFDs (fan + 2 pumps)
- **I2C Sensors** - ADS1115 for pressure and temperature
- **Calculated Values** - Heat load, flow rate, wet bulb, approach

## Architecture

```
FastAPI Backend (Port 8000)
├── main.py                 # FastAPI app, WebSocket, routes
├── fan_controller.py       # Fan PID with hysteresis
├── weather_service.py      # Weather.gov API client
├── calculations.py         # Heat load, wet bulb, etc.
│
├── Existing Hardware Modules (Reused)
├── vfd_controller.py       # Modbus RTU for VFDs
├── sensor_manager.py       # ADS1115 I2C sensors
└── pump_failover.py        # Pump redundancy logic
```

## Installation

### On Raspberry Pi

```bash
# 1. Copy backend files
scp -r backend/* pi@raspberrypi:/home/pi/backend/

# 2. Run installation script
ssh pi@raspberrypi
cd /home/pi/backend
sudo chmod +x install.sh
sudo ./install.sh
```

This will:
- Install Caddy reverse proxy
- Create Python virtual environment
- Install dependencies
- Set up systemd service
- Configure auto-start on boot

### Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Configuration

Edit `config.py` (from parent directory):

```python
# Serial/Modbus
SERIAL_PORT = '/dev/ttyUSB0'
SERIAL_BAUDRATE = 19200

# VFD Device IDs
VFD_CONFIG = {
    'fan': {'device_id': 1, ...},
    'pump_primary': {'device_id': 2, ...},
    'pump_backup': {'device_id': 3, ...}
}

# Sensors
SENSOR_CONFIG = {
    'i2c_address': 0x48,  # ADS1115
    ...
}
```

## API Documentation

Once running, access interactive API docs:

```
http://your-pi:8000/docs        # Swagger UI
http://your-pi:8000/redoc       # ReDoc
```

### WebSocket Endpoint

```javascript
const ws = new WebSocket('ws://your-pi:8000/ws');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('System status:', data);
    // Update UI
};
```

Sends full system status every 500ms:

```json
{
  "sensors": {
    "pressure_psi": 45.2,
    "basin_temp_f": 76.8,
    "timestamp": "2026-01-05T10:30:15",
    "status": "online"
  },
  "fan": {
    "state": "Running",
    "frequency": 35.5,
    "current": 12.3,
    "fault_code": 0
  },
  "weather": {
    "outdoor_temp_f": 42.0,
    "humidity_pct": 78.0,
    "wet_bulb_f": 35.4,
    "status": "online"
  },
  "calculated": {
    "return_temp_f": 88.2,
    "heat_load_kw": 45.6,
    "gpm": 60.0,
    "approach_f": 41.4
  },
  ...
}
```

### REST Endpoints

#### Status & Monitoring

```bash
# Get full system status
GET /api/status

# Get sensors only (fast)
GET /api/sensors

# Get VFD status (slow)
GET /api/vfds

# Get weather data
GET /api/weather

# Health check
GET /api/health
```

#### Fan Control

```bash
# Set mode (manual/auto)
POST /api/fan/mode
{"mode": "auto"}

# Set frequency (manual mode only)
POST /api/fan/setpoint
{"hz": 30.0}

# Configure auto mode
POST /api/fan/auto_config
{"target_temp": 75.0, "hysteresis": 5.0}
```

#### Pump Control

```bash
# Set pump frequency
POST /api/pump/frequency
{"hz": 45.0}

# Start active pump
POST /api/pump/start

# Stop pump
POST /api/pump/stop

# Switch active pump
POST /api/pump/switch
```

## Fan Auto Control Logic

Target: **75°F** with **5°F hysteresis**

```
Temp ≥ 80°F  →  Fan starts (PID: 20-60Hz)
Temp < 75°F  →  Fan stops
Between      →  Maintain current state

Anti-freeze: Fan forced OFF if basin < 45°F
```

PID Calculation:
```
freq = 20 + (temp_error × 2.0)
Clamped to 20-60 Hz range
```

## Heat Load Calculation

Uses Delta-T method:

```
GPM = (pump_hz / 60) × 80
ΔT = return_temp - basin_temp
Heat Load (kW) = (GPM × 500 × ΔT) / 3412
```

Where:
- **500** = water specific heat constant
- **3412** = BTU/hr to kW conversion
- **80 GPM** = estimated flow at 60Hz (20HP pump)

## Service Management

```bash
# Start service
sudo systemctl start cooling-tower

# Stop service
sudo systemctl stop cooling-tower

# Restart service
sudo systemctl restart cooling-tower

# View status
sudo systemctl status cooling-tower

# View live logs
sudo journalctl -u cooling-tower -f
```

## Troubleshooting

### Modbus Communication Issues

```bash
# Check serial port
ls -l /dev/ttyUSB*

# Test communication
python3 -c "from vfd_controller import *; ..."

# Check permissions
sudo usermod -a -G dialout pi
```

### I2C Sensor Issues

```bash
# Check I2C is enabled
sudo raspi-config nonint get_i2c

# Detect devices
sudo i2cdetect -y 1

# Should show 0x48 (ADS1115)
```

### Weather API Not Working

- Check internet connection
- Verify coordinates in `weather_service.py`
- Weather.gov may rate-limit (15min cache helps)
- System continues running with stale data

### WebSocket Disconnects

- Check nginx/Caddy timeout settings
- Verify firewall allows WebSocket upgrade
- Check client reconnection logic

## Development

```bash
# Run with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run tests (TODO)
pytest tests/

# Type checking
mypy main.py

# Linting
flake8 *.py
```

## Production Deployment

1. **Build React UI**
   ```bash
   cd /Users/max/Downloads/cooling-tower-scada-v6
   npm run build
   ```

2. **Deploy to Pi**
   ```bash
   scp -r dist/* pi@raspberrypi:/home/pi/cooling-tower-ui/dist/
   ```

3. **Restart services**
   ```bash
   sudo systemctl restart cooling-tower
   sudo systemctl restart caddy
   ```

4. **Access UI**
   ```
   http://your-pi/
   ```

## License

Proprietary - Internal Use Only
