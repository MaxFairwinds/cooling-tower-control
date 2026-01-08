# Cooling Tower SCADA System

Industrial cooling tower monitoring and control system using Raspberry Pi, GALT G540 VFDs, and modern web technologies.

## System Overview

**Current Status**: ✅ **PRODUCTION - PUBLICLY ACCESSIBLE**

### Deployment Architecture

**Public Access**:
- **React Dashboard**: http://159.89.150.146 (HTTP Basic Auth)
- **Flask Dashboard**: http://159.89.150.146:8001 (Flask login)
- **Username**: admin
- **Password**: cooling2025

**Infrastructure**:
- **Digital Ocean Droplet**: 159.89.150.146 (1GB RAM, Ubuntu 24.04)
  - Runs Caddy reverse proxy
  - Serves React frontend (static files)
  - Proxies API/WebSocket to Raspberry Pi
  - HTTP Basic Auth protection
- **Raspberry Pi**: 100.89.57.3 (Tailscale private network)
  - Runs FastAPI backend (port 8000)
  - Runs Flask dashboard (port 8001)
  - VFD control and sensor monitoring
  - Only accessible via Tailscale

**Network Flow**:
```
Internet → DO Droplet (Caddy) → Tailscale VPN → Raspberry Pi (Backend)
         159.89.150.146                          100.89.57.3
```

### Hardware Configuration

- **Raspberry Pi**: 100.89.57.3 (Tailscale), user: `max`
- **VFDs**: 3x GALT G540 (Modbus RTU @ 9600 baud)
  - ID 1: Tower Fan (CT-101)
  - ID 2: Primary Pump (P-101)
  - ID 3: Backup Pump (P-102)
- **Serial Interface**: USB to RS-485 converter @ /dev/ttyUSB0
- **Sensors**:
  - ADS1115 ADC @ I2C address 0x48
  - Channel 0: Pressure sensor (0-100 psi, 0-5V)
  - Channel 1: Temperature sensor
  - Channel 2: A2 sensor (unknown type - see A2_SENSOR_TECHNICAL_REPORT.md)

### Software Stack

#### Backend API (FastAPI - Port 8000) - READ-ONLY MODE
- **Status**: ✅ PRODUCTION
- **Location**: `/home/max/cooling-tower/backend/main_proxy.py`
- **Features**:
  - Proxies data from Flask dashboard (eliminates RS-485 conflicts)
  - ADS1115 sensor reading via I2C
  - Weather data integration (OpenWeatherMap)
  - WebSocket streaming @ 500ms intervals
  - REST API (read-only)
- **Note**: Uses `serial_lock.py` to prevent Modbus bus conflicts

#### Flask Dashboard (Port 8001)
- **Status**: ✅ PRODUCTION - VFD control interface
- **Location**: `/home/max/old_dashboard/web_dashboard.py`
- **Type**: Full control dashboard with authentication
- **Access**: http://159.89.150.146:8001 (admin/cooling2025)

#### React Frontend (Served from DO Droplet)
- **Status**: ✅ PRODUCTION
- **Framework**: Vite 6.4.1 + React + TypeScript
- **Location**: Digital Ocean `/var/www/cooling-tower/`
- **Features**:
  - Real-time SCADA visualization
  - SVG-based P&ID graphics
  - WebSocket live data streaming
  - Thermal profile charts
  - Read-only monitoring

#### Web Server (Digital Ocean Droplet)
- **Caddy**: Reverse proxy (publicly accessible)
- **Config**: `/etc/caddy/Caddyfile` (on DO droplet)
- **Routes**:
  - `/` → React frontend (static files)
  - `/ws` → WebSocket proxy to Pi
  - `/api/*` → REST API proxy to Pi
  - Port 8001 → Flask dashboard proxy to Pi
- **Security**: HTTP Basic Auth (admin/cooling2025)

## Quick Start

### SSH Access
```bash
# Raspberry Pi (via Tailscale)
ssh max@100.89.57.3
# Password: max123

# Digital Ocean Droplet
ssh phytocontrol  # (requires SSH config entry)
# or: ssh root@159.89.150.146
```

### Access Dashboards
- **React SCADA UI**: http://159.89.150.146 (admin/cooling2025)
- **Flask Control Dashboard**: http://159.89.150.146:8001 (admin/cooling2025)

### Start Backend on Pi (if needed)
```bash
ssh max@100.89.57.3
cd /home/max/cooling-tower/backend

# Start FastAPI backend (read-only proxy mode)
source venv/bin/activate
nohup python3 -m uvicorn main_proxy:app --host 0.0.0.0 --port 8000 > proxy.log 2>&1 &

# Start Flask dashboard (if not running)
cd /home/max/old_dashboard
nohup python3 web_dashboard.py > dashboard.log 2>&1 &
```

### Stop Backend
```bash
# Find processes
pgrep -f uvicorn
pgrep -f web_dashboard

# Kill them
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

### Initial Setup (Digital Ocean Droplet)

**1. Create Droplet**
- Size: 1GB RAM ($4-6/month)
- OS: Ubuntu 24.04 LTS
- Region: Any (closest to you)

**2. Install Tailscale**
```bash
ssh root@159.89.150.146
curl -fsSL https://tailscale.com/install.sh | sh
tailscale up
# Authorize in Tailscale admin console
```

**3. Install Caddy**
```bash
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
apt update && apt install -y caddy
```

**4. Deploy Caddyfile**
```bash
# Copy the Caddyfile from this repo
sudo nano /etc/caddy/Caddyfile
# Paste the configuration (see deployment/Caddyfile)
sudo systemctl restart caddy
```

### Updating Frontend (React UI)

```bash
# On local machine
cd frontend
npm run build

# Deploy to Digital Ocean droplet
rsync -avz --delete dist/ phytocontrol:/tmp/frontend-build/

# On droplet: move to web root
ssh phytocontrol
sudo cp -r /tmp/frontend-build/* /var/www/cooling-tower/
sudo chown -R caddy:caddy /var/www/cooling-tower
```

### Updating Backend on Pi

```bash
# Pull latest changes
ssh max@100.89.57.3
cd /home/max/cooling-tower
git pull

# Restart backend
pkill -f uvicorn
cd backend
source venv/bin/activate
nohup python3 -m uvicorn main_proxy:app --host 0.0.0.0 --port 8000 > proxy.log 2>&1 &
```

### Backend Dependencies (on Pi)
```bash
ssh max@100.89.57.3
cd /home/max/cooling-tower/backend
source venv/bin/activate
pip install -r requirements.txt
```

Key dependencies:
- FastAPI, uvicorn (web framework)
- httpx (for proxying Flask API)
- adafruit-circuitpython-ads1x15 (I2C sensors)
- pydantic >= 2.10.0 (Python 3.13 compatibility)
- RPi.GPIO (Raspberry Pi GPIO access)

## Network Configuration

### Raspberry Pi (Backend)
- **Tailscale IP**: 100.89.57.3 (private network only)
- **Port 8000**: FastAPI backend (uvicorn)
- **Port 8001**: Flask dashboard
- **SSH Port**: 22

### Digital Ocean Droplet (Reverse Proxy)
- **Public IP**: 159.89.150.146
- **Tailscale IP**: 100.94.101.123 (for Pi communication)
- **Port 80**: Caddy web server (React frontend + API proxy)
- **Port 8001**: Flask dashboard proxy
- **SSH Port**: 22

### Security
- HTTP Basic Auth on React frontend/API (admin/cooling2025)
- Flask dashboard has separate login (admin/cooling2025)
- Raspberry Pi only accessible via Tailscale VPN
- Caddy stopped on Pi (no longer needed)

## Development Workflow

### Local Development
```bash
# Terminal 1: Ensure backend is running on Pi
ssh max@100.89.57.3
pgrep -f uvicorn  # Check if running

# Terminal 2: Run frontend locally
cd frontend
VITE_WS_URL=ws://159.89.150.146/ws VITE_API_URL=http://159.89.150.146 npm run dev
# Access at http://localhost:5173
```

### Production Deployment
1. **Test changes locally**
2. **Update frontend .env.production** (if needed)
   ```bash
   # frontend/.env.production
   VITE_WS_URL=ws://159.89.150.146/ws
   VITE_API_URL=http://159.89.150.146
   ```
3. **Build and deploy frontend**:
   ```bash
   cd frontend
   npm run build
   rsync -avz --delete dist/ phytocontrol:/tmp/frontend-build/
   ssh phytocontrol "sudo cp -r /tmp/frontend-build/* /var/www/cooling-tower/"
   ```
4. **Update backend** (if needed):
   ```bash
   ssh max@100.89.57.3
   cd /home/max/cooling-tower
   git pull
   pkill -f uvicorn
   cd backend && source venv/bin/activate
   nohup python3 -m uvicorn main_proxy:app --host 0.0.0.0 --port 8000 > proxy.log 2>&1 &
   ```
5. **Test**: http://159.89.150.146

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
- **Pi Backend**: `/home/max/cooling-tower/backend/proxy.log`
- **Pi Flask**: `/home/max/old_dashboard/dashboard.log`
- **DO Caddy**: `/var/log/caddy/access.log`
- **DO Caddy (Flask)**: `/var/log/caddy/flask.log`
- **System**: `journalctl -u caddy` (on DO droplet)

### Troubleshooting
1. **Site not accessible**: 
   - Check if Caddy is running on DO: `ssh phytocontrol "systemctl status caddy"`
   - Check Tailscale connection: `ssh phytocontrol "tailscale status"`
2. **Backend not responding**: 
   - Check Pi backend: `ssh max@100.89.57.3 "pgrep -af uvicorn"`
   - Check logs: `ssh max@100.89.57.3 "tail -f /home/max/cooling-tower/backend/proxy.log"`
3. **VFD communication errors**: 
   - SSH to Pi: `ssh max@100.89.57.3`
   - Check Flask dashboard (has direct VFD access)
   - Verify USB adapter: `ls /dev/ttyUSB*`
4. **Sensor reading errors**: 
   - Check I2C: `i2cdetect -y 1`
5. **Authentication not working**:
   - Verify basic auth hash in Caddyfile
   - Test: `curl -u admin:cooling2025 http://159.89.150.146/api/health`

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
