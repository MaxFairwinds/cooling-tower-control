# RS485 Modbus Communication Issue - Technical Summary

**Date:** December 16, 2025  
**Hardware:** Raspberry Pi 4 → Waveshare USB-RS485 → WEG CFW300 VFD

---

## Hardware Configuration

### Waveshare USB-RS485 Adapter
- **Model:** USB TO RS485 (Industrial Grade)
- **Chips:** FT232RL (USB-Serial) + SP485E (RS485 Transceiver)
- **Features:** Hardware automatic direction control, onboard 120Ω termination
- **Specifications:** 300-921600 baud, industrial rated, explicitly supports Modbus
- **Device:** /dev/ttyUSB0 on Raspberry Pi

### WEG CFW300 VFD
- **Model:** CFW300, single-phase 208V
- **Communication:** RS485 Modbus RTU slave
- **Configuration:**
  - P202 = 3 (Serial mode - confirmed on display)
  - P220 = 6 (Serial REM)
  - P221 = 9 (Serial speed reference)
  - P308 = 1 (Modbus address 1)
  - P310 = 1 (19200 baud)
  - P311 = 1 (8E1: 8 data, even parity, 1 stop)
  - P312 = 2 (Modbus RTU Slave)
  - P316 = 0 (Communication status - remains zero)
- **Termination:** Two switches, both DOWN = ON (120Ω active)

### Wiring
- A-to-A (Adapter A+ to VFD A terminal)
- B-to-B (Adapter B- to VFD B terminal)  
- GND-to-GND (Common ground reference)

---

## Voltage Measurements & Discovery

### Initial Problem
Standard Modbus communication attempts produced inadequate voltage:
- **Unloaded (no VFD):** ~2.6V initially, but inconsistent
- **With VFD connected:** Dropped to 0.5V or lower
- **RS485 Spec Minimum:** 1.5V differential for reliable communication

### Critical Discovery: Voltage vs. Transmission Pattern

| Test Script | Transmission Pattern | Voltage (with VFD) | Result |
|-------------|---------------------|-------------------|---------|
| test_vfd_modbus.py | 8-byte Modbus packets, 50ms gaps | 0.44V | Single 0x00 response |
| test_rapid_fire.py | 8-byte Modbus packets, 10ms gaps | 0.47V | Single 0x00 response |
| test_waveshare_voltage.py | Continuous 100-byte 0xFF stream, 1ms gaps | 1.93V | No response (drowns VFD) |

**Key Finding:** Voltage is directly proportional to transmission duty cycle. The adapter requires near-continuous data transmission to maintain adequate voltage levels.

---

## Current Status

### What Works
✓ Waveshare adapter produces 1.93V with continuous high-frequency transmission  
✓ VFD parameters correctly configured and verified on display  
✓ GND connection improves voltage from 0.5V to 1.93V  
✓ Hardware automatic direction control functions (no manual RTS/DTR needed)  
✓ Wiring verified correct (A-A, B-B, GND-GND)  

### What Doesn't Work
✗ Standard Modbus packet transmission produces only 0.44V  
✗ VFD responds with single 0x00 byte (not valid Modbus response)  
✗ P316 remains at 0 (VFD not detecting valid communication)  
✗ Continuous transmission maintains voltage BUT blocks reception  

---

## The Fundamental Challenge

**The Problem:** This appears to be a half-duplex protocol conflict:

1. **To maintain 1.93V:** Need continuous transmission (background thread writing data constantly)
2. **To receive from VFD:** Must stop transmitting and listen
3. **These requirements are mutually exclusive**

### Attempted Solutions

#### Approach 1: Background Voltage Keeper
```python
# Background thread continuously writes 0xFF
# Foreground attempts Modbus communication
```
**Result:** Maintains 1.93V but receives NOTHING (background drowns out VFD response)

#### Approach 2: Standard Modbus Timing
```python
# Send packet, wait for response
# 8 bytes every 10-50ms
```
**Result:** Voltage drops to 0.44V, VFD responds with single 0x00 byte (corrupted)

#### Approach 3: Rapid-Fire Modbus
```python
# Send packets continuously with minimal gaps
# 8 bytes every 10ms
```
**Result:** Voltage only reaches 0.47V, still inadequate

---

## Technical Questions

### 1. Why does voltage depend on transmission duty cycle?
- RS485 transmitter should maintain differential voltage regardless
- Could this indicate:
  - Insufficient USB power delivery to RS485 driver chip?
  - Capacitive loading requiring constant charge?
  - Weak SP485E driver design?
  - Hardware automatic control too aggressive in disabling driver?

### 2. Why single 0x00 byte response?
- Consistent across all baud rates (9600-115200)
- Consistent across all RTS/DTR combinations
- Not present without transmission (not noise)
- Not echo of transmitted data (verified with test pattern)
- Suggests VFD is attempting to respond but signal too weak/corrupted

### 3. Is this a known limitation?
- Waveshare documentation explicitly states Modbus support
- Device is industrial-rated
- Yet standard Modbus timing produces inadequate voltage

---

## Test Data

### Voltage Test (test_waveshare_voltage.py)
```python
# Continuous transmission: b'\xFF' * 100, 1ms delay
# Measured: 1.93V at adapter terminals with VFD connected
```

### Modbus Test (test_rapid_fire.py)
```python
# Modbus packet: 01 03 00 01 00 01 D5 CA (Read P001)
# Frequency: Every 10ms
# Measured: 0.47V at adapter terminals with VFD connected
# Response: Single 0x00 byte consistently
```

### Communication Status
- **VFD P316:** Remains at 0 (no valid communication detected)
- **LED Activity:** TXD lights on adapter, no RXD activity
- **Response Pattern:** Always exactly 1 byte: 0x00

---

## Hardware Verification

### Waveshare Adapter
- EEPROM factory restored on Mac (stable)
- CBUS0 = CLK12 (0x08) verified
- FT232RL operating correctly
- Device recognized: VID:0403 PID:6001

### VFD Configuration
- All parameters triple-checked on display panel
- P202 = 3 verified multiple times (Serial mode)
- Baud rate P310 = 1 confirmed (19200)
- No error codes on VFD display
- VFD powered and operational

---

## Questions for Review

1. **Is there a way to maintain voltage while allowing receive windows?**
   - Can we pulse high-frequency data between Modbus packets?
   - Is there a different RS485 timing strategy?

2. **Is this voltage behavior normal for SP485E transceivers?**
   - Should we expect voltage to drop during transmit idle periods?
   - Is continuous loading required for differential voltage?

3. **Could this be a USB power delivery issue?**
   - Should we try external 5V power to RS485 chip?
   - Is the Pi USB port providing sufficient current?

4. **Is the onboard 120Ω termination the problem?**
   - Two 120Ω resistors in parallel = 60Ω load
   - Could this be overloading a weak transmitter?
   - Is there a way to disable Waveshare's termination?

5. **Alternative approaches?**
   - Different transmission patterns?
   - Different Modbus timing parameters?
   - Firmware/EEPROM tweaks to FT232RL?

---

## Files for Reference

### Working Voltage Script
- **test_waveshare_voltage.py** - Produces 1.93V via continuous transmission
- Located: ~/test_waveshare_voltage.py on Pi

### Failed Modbus Scripts  
- **test_vfd_modbus.py** - Basic Modbus read (0.44V)
- **test_rapid_fire.py** - Continuous Modbus packets (0.47V)
- **test_hardware_auto.py** - Hardware auto control test (0.44V)

### All scripts available on Raspberry Pi at ~/
- SSH access: coolingtower.local
- User: max

---

## Summary

We have a fully functional hardware setup (adapter, VFD, wiring) that is properly configured. The adapter CAN produce adequate voltage (1.93V) when transmitting continuously, but standard Modbus communication patterns produce inadequate voltage (0.44-0.47V) resulting in corrupted VFD responses. 

The challenge is finding a transmission strategy that:
1. Maintains ≥1.5V differential voltage
2. Allows proper receive windows for VFD responses
3. Works within Modbus RTU protocol constraints

This appears to be a fundamental incompatibility between the adapter's voltage characteristics and standard Modbus half-duplex timing, despite the adapter being explicitly marketed for Modbus applications.
