# CFW300 Test Environment - Setup Verification

## ✅ Verification Complete

**Date**: December 3, 2025  
**Pi**: coolingtower.local (192.168.5.96)

## Setup Status

### Directory Structure
```
/home/max/
├── venv/                    # Python virtual environment
└── test_cfw300/            # CFW300 test environment
    ├── config_cfw300.py
    ├── vfd_controller_cfw300.py
    ├── test_suite.py
    ├── interactive_test.py
    └── README_CFW300.md
```

### Files Deployed
- ✅ `config_cfw300.py` (2.5 KB) - CFW300 configuration
- ✅ `vfd_controller_cfw300.py` (7.3 KB) - VFD controller
- ✅ `test_suite.py` (7.2 KB) - Automated tests
- ✅ `interactive_test.py` (4.3 KB) - Manual control
- ✅ `README_CFW300.md` (3.8 KB) - Documentation

### Python Environment
- ✅ Python 3.13.5 installed
- ✅ Virtual environment active at `/home/max/venv`
- ✅ pymodbus 3.11.3 installed
- ✅ adafruit-circuitpython-ads1x15 installed
- ✅ All imports successful

### Hardware Configuration
- ✅ UART enabled (`enable_uart=1` in `/boot/firmware/config.txt`)
- ⚠️ **REBOOT REQUIRED** for serial port to become available
- 🔄 After reboot: `/dev/ttyS0` or `/dev/ttyAMA0` will be available

### Configuration
- ✅ Device IDs: 101, 102, 103
- ✅ Serial port: /dev/ttyS0 (will be available after reboot)
- ✅ Baudrate: 9600
- ✅ CFW300 registers mapped (P682, P681, P683)

## ⚠️ IMPORTANT: Reboot Required

The UART was disabled and has now been enabled. **You must reboot the Pi** for the serial port to become available.

**Reboot command:**
```bash
ssh max@coolingtower.local
sudo reboot
```

Wait ~30 seconds, then reconnect.

## Ready to Test (After Reboot)

### Quick Test Commands

**SSH to Pi:**
```bash
ssh max@coolingtower.local
cd test_cfw300
source ../venv/bin/activate
```

**Verify serial port exists:**
```bash
ls -l /dev/ttyS0
# or
ls -l /dev/ttyAMA0
```

**Run automated test suite:**
```bash
python3 test_suite.py
```

**Run interactive test:**
```bash
python3 interactive_test.py
```

## Before Testing

Configure CFW300 parameters:
- P220 = Serial (command source)
- P221 = Serial (speed reference)
- P300 = 101 (device ID)
- P301 = 9600 (baud rate)
- P302 = 0 (no parity)
- P313 = 1 (stop on comm loss)

Wire RS-485:
- Pi A+ → CFW300 A+
- Pi B- → CFW300 B-

## Next Steps

1. **Reboot the Pi** (`sudo reboot`)
2. Verify serial port exists (`ls -l /dev/ttyS0`)
3. Configure CFW300 parameters
4. Connect RS-485 wiring
5. Run `python3 test_suite.py`
6. Verify all tests pass
7. Use `python3 interactive_test.py` for manual exploration

---

**Status**: ✅ Setup complete - **REBOOT REQUIRED**
