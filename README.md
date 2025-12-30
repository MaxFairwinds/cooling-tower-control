# Cooling Tower Control System

Industrial cooling tower automation with Raspberry Pi 4 controlling 3 GALT G540 VFDs via Modbus RTU.

## Hardware
- Raspberry Pi 4
- 3x GALT G540 VFDs (Fan + 2 Pumps)
- Waveshare USB-RS485
- ADS1115 ADC with NTC thermistor and PSU-GP100-6 pressure sensor

## Features
- Web dashboard with authentication
- Automatic pressure-based control
- Pump failover management
- Remote access via Tailscale

## Quick Start
```bash
./start_dashboard.sh
```
Access: https://coolingtower.tailc1d288.ts.net/
