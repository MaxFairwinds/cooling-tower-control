# Cooling Tower SCADA System

Industrial cooling tower monitoring and control system using Raspberry Pi, GALT G540 VFDs, and modern web technologies.

## System Overview

**Current Status**: Production deployment with Flask dashboard (operational), FastAPI backend (development)

### Hardware Configuration

- **Raspberry Pi**: 100.89.57.3 (user: `max`)
- **VFDs**: 3x GALT G540 (Modbus RTU @ 9600 baud)
  - ID 1: Tower Fan (CT-101)
  - ID 2: Primary Pump (P-101)
  - ID 3: Backup Pump (P-102)
- **Serial Interface**: USB to RS-485 converter @ /dev/ttyUSB0
- **Sensors**:
  - ADS1115 ADC @ I2C address 0x48
  - Channel 0: Pressure sensor (0-100 psi, 0-5V) - *not yet wired*
  - Channel 1: Temperature sensor (placeholder calibration)

### Software Stack

#### Backend (Python 3.13)
- **FastAPI**: Modern async web framework with WebSocket support
- **Location**: `/home/max/cooling-tower/backend/`
- **Port**: 8000 (when running)
- **Features**:
  - Modbus RTU communication with G540 VFDs
  - ADS1115 sensor reading via I2C
  - Weather data integration (OpenWeatherMap)
  - WebSocket streaming @ 500ms intervals
  - REST API for control operations

#### Legacy Dashboard (Flask)
- **Location**: `/home/max/old_dashboard/`
- **Port**: 8001 (currently active)
- **Status**: Production backup system

#### Frontend (React + TypeScript)
- **Framework**: Vite 6.4.1 + React
- **Location**: `/home/max/cooling-tower/frontend/`
- **Features**:
  - Real-time SCADA visualization
  - SVG-based P&ID graphics
  - WebSocket live data streaming
  - Thermal profile charts
  - VFD control panels

#### Web Server
- **Caddy**: Reverse proxy on port 80
- **Config**: `/etc/caddy/Caddyfile`
- **Routes**:
  - `/` → Frontend static files
  - `/ws` → WebSocket proxy to backend
  - `/api/*` → REST API proxy to backend

## Quick Start

### SSH Access
```bash
ssh max@100.89.57.3
# Password: max123
```

### Start Backend (FastAPI)
```bash
cd /home/max/cooling-tower/backend
source venv/bin/activate
nohup python3 main.py > server.log 2>&1 &
```

### Access Dashboards
- **Flask Dashboard**: http://100.89.57.3:8001
- **New SCADA UI**: http://100.89.57.3 (requires backend running)

### Stop Backend
```bash
# Find process
ps aux | grep "python3 main.py"
# Kill it
kill <PID>
```

## Project Structure

```
insider workspace/
├── backend/                    # FastAPI backend
│   ├── main.py                # Main application entry point
│   ├── modbus_vfd_test.py     # VFD communication module
│   ├── sensor_manager.py      # ADS1115 sensor interface
│   ├── weather_service.py     # Weather data integration
│   ├── calculations.py        # Thermal calculations
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React SCADA UI
│   ├── App.tsx                # Main application component
│   ├── hooks/
│   │   └── useWebSocket.ts    # WebSocket connection hook
│   ├── components/scada/      # SVG visualization components
│   ├── lib/api.ts             # API client
│   └── .env.production        # Production config (Pi IP)
│
├── old_dashboard/              # Legacy Flask dashboard
│   └── web_dashboard.py       # Flask app on port 8001
│
├── docs/                       # Current documentation
│   ├── G540_QUICK_START.md    # VFD setup guide
│   └── G540_TECHNICAL_SUMMARY.md
│
├── CFW300_Archive/             # Old WEG CFW300 testing (not used)
├── diagnostics/                # Diagnostic scripts
└── hardware_manuals/           # Equipment documentation
```

## Deployment

### Building Frontend
```bash
# On local machine
cd frontend
npm run build
rsync -avz --delete dist/ max@100.89.57.3:/home/max/cooling-tower/frontend/dist/
```

### Backend Dependencies
```bash
ssh max@100.89.57.3
cd /home/max/cooling-tower/backend
source venv/bin/activate
pip install -r requirements.txt
```

Key dependencies:
- FastAPI, uvicorn (web framework)
- pyserial (Modbus RTU)
- adafruit-circuitpython-ads1x15 (I2C sensors)
- pydantic >= 2.10.0 (Python 3.13 compatibility)
- RPi.GPIO (Raspberry Pi GPIO access)

## Network Configuration

- **Pi IP**: 100.89.57.3
- **SSH Port**: 22
- **Flask Dashboard**: 8001
- **FastAPI Backend**: 8000
- **Caddy Web Server**: 80
- **Frontend Dev Server**: 3000 (local only)

## Development Workflow

### Local Development
```bash
# Terminal 1: Run backend on Pi
ssh max@100.89.57.3
cd /home/max/cooling-tower/backend
source venv/bin/activate
python3 main.py

# Terminal 2: Run frontend locally
cd frontend
VITE_WS_URL=ws://100.89.57.3/ws VITE_API_URL=http://100.89.57.3 npm run dev
# Access at http://localhost:3000
```

### Production Deployment
1. Test changes locally
2. Build frontend: `npm run build`
3. Deploy: `rsync -avz --delete dist/ max@100.89.57.3:/home/max/cooling-tower/frontend/dist/`
4. Restart backend if needed
5. Access at http://100.89.57.3

## VFD Communication

### Modbus RTU Configuration
- **Baud Rate**: 9600
- **Data Bits**: 8
- **Parity**: None
- **Stop Bits**: 1
- **Device**: /dev/ttyUSB0

### G540 Register Map (key registers)
- `0x0000`: Frequency setpoint (0-6000 = 0-60.00 Hz)
- `0x0001`: Run/Stop command (1=Run, 0=Stop)
- `0x0002`: Current frequency (read-only)
- `0x0003`: Motor current (read-only)
- `0x0004`: Fault code (read-only)

See [docs/G540_TECHNICAL_SUMMARY.md](docs/G540_TECHNICAL_SUMMARY.md) for complete register reference.

## Known Issues & To-Do

### Sensors
- [ ] Wire pressure sensor to ADS1115 Channel 0
- [ ] Calibrate temperature sensor (currently using placeholder formula)
- [ ] Verify sensor voltage levels (0-5V to 0-3.3V conversion)

### Software
- [ ] Add read-only mode toggle in UI
- [ ] Implement user authentication
- [ ] Add data logging and trend charts
- [ ] Complete error handling for VFD communication
- [ ] Add automatic pump failover logic

### Hardware
- [ ] Install pressure sensor on cooling tower basin
- [ ] Verify temperature sensor type and update conversion
- [ ] Test VFD emergency stop circuit
- [ ] Add flow meter on pump discharge

## Safety Notes

⚠️ **IMPORTANT**: This system controls industrial equipment. Always:
- Verify all safety interlocks before enabling automatic control
- Test manual overrides regularly
- Monitor VFD fault codes
- Keep emergency stop button accessible
- Never disable safety limits without documented reason

## Support & Maintenance

### Logs
- Backend: `/home/max/cooling-tower/backend/server.log`
- Caddy: `/var/log/caddy/access.log`
- System: `journalctl -u caddy`

### Troubleshooting
1. **Backend not responding**: Check if process is running (`ps aux | grep main.py`)
2. **VFD communication errors**: Verify USB RS-485 adapter (`ls /dev/ttyUSB*`)
3. **Sensor reading errors**: Check I2C devices (`i2cdetect -y 1`)
4. **Frontend not loading**: Verify Caddy is running (`systemctl status caddy`)

### VFD Reset
If VFD is in fault state:
```python
# SSH to Pi
python3
from modbus_vfd_test import write_g540_frequency
write_g540_frequency('/dev/ttyUSB0', vfd_id=1, hz=0)  # Stop fan
# Check fault code, clear if needed, then restart
```

## Repository

GitHub: https://github.com/MaxFairwinds/cooling-tower-control

## License

Internal project - All rights reserved
