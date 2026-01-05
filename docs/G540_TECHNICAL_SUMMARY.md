# GALT G540 VFD Setup - Technical Summary

## Project Status: Ready for Testing

**Date**: December 22, 2024  
**Hardware**: GALT G540 VFD + Raspberry Pi 4 + Waveshare USB-RS485  
**Objective**: RS485 Modbus RTU communication for VFD control

---

## Background

After extensive troubleshooting with WEG CFW300 VFDs (defective CRS485 module, mainboard connector issues), we have pivoted to the GALT G540 VFD which is a known working unit.

---

## Manual Analysis Complete

**Source**: `galt_g500manual.pdf` (417 pages)
- Confirmed G540 model coverage (pages 17-19)
- Extracted Modbus RTU protocol specification (Chapter 9, pages 309-325)
- Identified all register addresses and communication parameters

---

## Default Communication Settings

From GALT G500 manual defaults:

| Parameter | Setting | Description |
|-----------|---------|-------------|
| **P14.00** | 1 | Slave address |
| **P14.01** | 4 | Baud rate = 19200 bps |
| **P14.02** | 1 | Parity = Even, 8 data bits, 1 stop bit |
| **P14.03** | 5 ms | Response delay |
| **P14.04** | 0.0 s | Timeout (disabled) |

**Critical**: To enable Modbus control:
- **P00.01** = 2 (Communication control)
- **P00.02** = 0 (Modbus/Modbus TCP channel)

---

## Modbus Register Map

### Key Registers Identified

#### Control (Write)
- **0x2000**: Control command (0x0001=Forward, 0x0005=Stop, 0x0007=Fault reset)
- **0x2001**: Frequency setting (units: 0.01 Hz, e.g., 1000 = 10.00 Hz)

#### Status (Read)
- **0x2100**: State word 1 (running/stopped/fault)
- **0x2101**: State word 2 (ready, control mode, motor number)
- **0x2102**: Fault code
- **0x2103**: Identification (should return 0x01A1 for G500 series)

#### Monitoring (Read)
- **0x3000**: Running frequency (0.01 Hz)
- **0x3001**: Set frequency (0.01 Hz)
- **0x3002**: Bus voltage (0.1 V)
- **0x3003**: Output voltage (1 V)
- **0x3004**: Output current (0.1 A)
- **0x3005**: Rotating speed (RPM)
- **0x3006**: Output power (0.1 %)
- **0x3007**: Output torque (0.1 %)

#### Parameters (Read/Write)
- **0x0001**: P00.01 (Command channel)
- **0x0002**: P00.02 (Communication channel)
- **0x1400**: P14.00 (Slave address)
- **0x1401**: P14.01 (Baud rate)
- **0x1402**: P14.02 (Parity)

---

## Register Addressing Formula

**GALT G500**: 
```
Register Address = (Group << 8) | Parameter_within_group

Examples:
P00.01 → (0x00 << 8) | 0x01 = 0x0001
P14.00 → (0x14 << 8) | 0x00 = 0x1400
P14.01 → (0x14 << 8) | 0x01 = 0x1401
```

**This is DIFFERENT from CFW300** where P001 = register 1 directly.

---

## Diagnostic Script Created

**File**: `g540_diagnostic.py`

**Features**:
- Tests basic communication (reads identification 0x01A1)
- Reads VFD configuration (P00.01, P00.02, P14.00-P14.02)
- Reads VFD status (state words, fault code)
- Reads measurements (frequency, voltage, current, RPM, power, torque)
- Optional control test sequence (set frequency, start forward, stop)

**Location**:
- Local: `/Users/max/insider workspace/g540_diagnostic.py`
- Raspberry Pi: `~/g540_diagnostic.py`

---

## Quick Start Guide Created

**File**: `G540_QUICK_START.md`

Contains:
- Hardware wiring instructions
- Default communication settings
- Critical parameter setup
- Register map summary
- Python code examples
- Troubleshooting guide
- Manual page references

---

## Next Steps

### 1. Hardware Connection
```
Waveshare USB-RS485 → GALT G540
     A (D+)         →    A (D+)
     B (D-)         →    B (D-)
     GND            →    GND
120Ω termination ON both ends
```

### 2. Run Diagnostic
```bash
ssh max@coolingtower.local
python3 ~/g540_diagnostic.py
```

### 3. Expected First Test Results
- ✓ Identification: 0x01A1 (confirms G500 series)
- ✓ P14.00 = 1 (slave address)
- ✓ P14.01 = 4 (19200 baud)
- ✓ P14.02 = 1 (Even parity)
- ✓ State word shows current status
- ✓ Bus voltage shows ~300V DC

### 4. Enable Modbus Control (if needed)
Using VFD keypad or HMI:
1. Set P00.01 = 2 (Communication control)
2. Set P00.02 = 0 (Modbus channel)
3. Re-run diagnostic with control test enabled

### 5. Develop Application Code
Once basic communication confirmed:
- Create control application
- Implement frequency ramping
- Add safety interlocks
- Build monitoring dashboard

---

## Key Advantages Over CFW300

1. **No CRS485 module required** - Built-in RS485
2. **Better documentation** - Complete register map in manual
3. **Standard addressing** - Clean register formula
4. **Identification register** - Can verify VFD model via Modbus
5. **Read/write control** - Control register (0x2000) is R/W, not write-only
6. **Known working unit** - User confirmed G540 works

---

## Lessons from CFW300 Experience

1. ✓ **Hardware verification first** - Use resistance/voltage testing
2. ✓ **Loopback tests** - Proved Waveshare adapters work perfectly
3. ✓ **Manual reading** - Register addressing critical
4. ✓ **Start simple** - Read identification before complex operations
5. ✓ **Document everything** - Track all parameter changes

---

## Files Created

### Scripts
- [x] `g540_diagnostic.py` - Comprehensive diagnostic tool
  - Location: Local + Raspberry Pi `~/`
  - Tests: Basic comm, config, status, measurements, control

### Documentation
- [x] `G540_QUICK_START.md` - Quick reference guide
  - Hardware setup
  - Register map
  - Code examples
  - Troubleshooting

- [x] `G540_TECHNICAL_SUMMARY.md` - This document
  - Complete project status
  - Manual analysis results
  - Next steps

### Reference Material
- [x] `galt_g500manual.pdf` - 417-page manual
  - Chapter 9: Modbus protocol
  - P14 group: Communication parameters
  - Register maps and examples

---

## Archived CFW300 Materials

All CFW300 work preserved in:
- **Local**: `CFW300_Archive/` (43 Python scripts, 3 manuals, technical summary)
- **Raspberry Pi**: `~/CFW300_Archive/` (66 Python scripts)

Reason for archival: Hardware failures (defective CRS485 module, VFD mainboard connector issues on both units tested)

---

## Success Criteria

Communication successful when:
- [x] Script created and transferred to Pi
- [ ] VFD responds with identification 0x01A1
- [ ] Configuration parameters readable
- [ ] State words show valid status
- [ ] Measurements show realistic values
- [ ] Control commands accepted (when P00.01=2)
- [ ] Motor responds to start/stop (when properly configured)

---

## Support Resources

1. **Manual**: `galt_g500manual.pdf`
   - Page 218-220: P14 communication parameters
   - Page 309-325: Modbus protocol chapter
   - Page 320-322: Register address tables

2. **Scripts**: 
   - `g540_diagnostic.py` - Full diagnostic
   - `compare_adapters.py` - Adapter comparison (if needed)
   - `modbus_vfd_test.py` - Generic VFD test (reference)

3. **Documentation**:
   - `G540_QUICK_START.md` - Quick reference
   - `G540_TECHNICAL_SUMMARY.md` - This document

---

## Notes

- G540 uses **19200 baud by default**, not 9600
- Register addressing uses **group << 8 | param** formula
- **P00.01=2 and P00.02=0** required for Modbus control
- Control register **0x2000 is R/W**, not write-only like CFW300
- Identification register **0x2103** enables VFD model verification

---

**Status**: ✅ **READY FOR HARDWARE TESTING**

All software prepared. Next action: Connect hardware and run `g540_diagnostic.py`
