# RaspCoolingTower

Raspberry Pi-based control system for cooling tower with **3 VFDs** and automatic pump failover.

## Quick Start

### Deploy Code to Pi
```bash
./manage.sh deploy
```

### Run 10-Second Test
```bash
./manage.sh test
```

### Run Control System
```bash
./manage.sh run
```

### View Logs
```bash
./manage.sh logs
```

### SSH to Pi
```bash
./manage.sh shell
```

## System Overview

**Hardware:**
- Raspberry Pi 4B (`coolingtower.local`)
- Waveshare RS-485/CAN HAT
- **3x Galt G540 VFDs** on shared RS-485 bus:
  - Device ID 1: Cooling Tower Fan Motor
  - Device ID 2: Primary Pump Motor  
  - Device ID 3: Backup Pump Motor (automatic failover)
- ADS1115 16-bit ADC
- PSU-GP100-6 Pressure Transducer (0-100 psi)

**Software:**
- Python 3.13
- pymodbus 3.11.3 (Modbus RTU)
- adafruit-circuitpython-ads1x15 (ADC interface)

**Features:**
- Multi-VFD control on single RS-485 bus
- Automatic pump failover (primary → backup)
- Pressure-based pump speed control
- Health monitoring and error tracking

## Project Structure

```
├── config.py            # System configuration
├── vfd_controller.py    # Multi-VFD Modbus control
├── pump_failover.py     # Automatic pump failover
├── sensor_manager.py    # Sensor reading (ADS1115)
├── main_control.py      # Main control loop
├── manage.sh            # Management script
├── deploy_code.sh       # Deployment helper
└── remote_setup.sh      # Initial Pi setup
```

## Documentation

- **[Implementation Plan](file:///Users/max/.gemini/antigravity/brain/ce2ba2f1-64f4-407d-a045-795f699d9880/implementation_plan.md)** - Technical design
- **[Walkthrough](file:///Users/max/.gemini/antigravity/brain/ce2ba2f1-64f4-407d-a045-795f699d9880/walkthrough.md)** - Setup and verification results
- **[Tasks](file:///Users/max/.gemini/antigravity/brain/ce2ba2f1-64f4-407d-a045-795f699d9880/task.md)** - Implementation checklist

## Important Notes

> [!WARNING]
> **VFD Configuration Required**
> 
> 1. Each VFD must be configured with a unique Modbus device ID:
>    - Fan Motor: Device ID = 1
>    - Primary Pump: Device ID = 2
>    - Backup Pump: Device ID = 3
> 2. Register addresses in `vfd_controller.py` are placeholders - verify with Galt G540 manual
> 3. Add 120Ω termination resistors at both ends of RS-485 bus

> [!IMPORTANT]
> **Next Steps Before Going Live:**
> 1. Wire all 3 VFDs to RS-485 bus (parallel A+/B- connections)
> 2. Configure each VFD with correct device ID
> 3. Wire ADS1115 to pressure transducer
> 4. Verify VFD register addresses from manual
> 5. Test pump failover logic
> 6. Tune control parameters in `config.py`

## Status

✅ Code deployed and tested on Pi  
✅ All dependencies installed  
✅ Modbus communication framework working  
⏳ Awaiting VFD connection for live testing
