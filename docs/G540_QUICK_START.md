# GALT G540 VFD Modbus Quick Start Guide

## Hardware Setup

### Wiring
Connect RS485 adapter to G540 VFD:
- **A (D+)** → **A (D+)**
- **B (D-)** → **B (D-)**
- **GND** → **GND**
- Enable 120Ω termination on BOTH ends

### Default Communication Settings (G500 Series)
- **Baud Rate**: 19200 bps (P14.01 = 4)
- **Parity**: Even, 8 data bits, 1 stop bit (P14.02 = 1)
- **Slave Address**: 1 (P14.00)
- **Protocol**: Modbus RTU

## Critical Parameters for Modbus Control

### Enable Communication Control
```
P00.01 = 2          // Running command channel = Communication
P00.02 = 0          // Communication running command channel = Modbus
```

## Running the Diagnostic

### On Raspberry Pi:
```bash
python3 ~/g540_diagnostic.py
```

### Expected Results:
1. **Identification**: Should return 0x01A1 (GALT G500 series)
2. **Configuration**: Should show current P14.xx settings
3. **Status**: Should show "Stopped" or "Ready to run"
4. **Measurements**: Should show bus voltage, frequencies, etc.

## Modbus Register Map Summary

### Control Registers (Write)
| Register | Function | Values |
|----------|----------|--------|
| 0x2000 | Control command | 0x0001=Forward, 0x0005=Stop, 0x0007=Fault reset |
| 0x2001 | Frequency setting | Units: 0.01 Hz (1000 = 10.00 Hz) |

### Status Registers (Read)
| Register | Function | Units |
|----------|----------|-------|
| 0x2100 | State word 1 | 0x0001=Forward, 0x0003=Stopped, 0x0004=Fault |
| 0x2101 | State word 2 | Bit field (ready, motor#, control mode) |
| 0x2102 | Fault code | 0x0000=No fault |
| 0x2103 | Identification | 0x01A1=G500 series |

### Monitoring Registers (Read)
| Register | Function | Scale | Units |
|----------|----------|-------|-------|
| 0x3000 | Running frequency | 0.01 | Hz |
| 0x3001 | Set frequency | 0.01 | Hz |
| 0x3002 | Bus voltage | 0.1 | V |
| 0x3003 | Output voltage | 1.0 | V |
| 0x3004 | Output current | 0.1 | A |
| 0x3005 | Rotating speed | 1.0 | RPM |
| 0x3006 | Output power | 0.1 | % |
| 0x3007 | Output torque | 0.1 | % |

### Parameter Registers (Read/Write)
| Register | Function | Values |
|----------|----------|--------|
| 0x0001 | P00.01: Command channel | 0=Keypad, 1=Terminal, 2=Communication |
| 0x0002 | P00.02: Comm channel | 0=Modbus/Modbus TCP |
| 0x1400 | P14.00: Slave address | 1-247 |
| 0x1401 | P14.01: Baud rate | 0=1200, 1=2400, 2=4800, 3=9600, 4=19200, 5=38400, 6=57600, 7=115200 |
| 0x1402 | P14.02: Parity | 0=N,8,1  1=E,8,1  2=O,8,1  3=N,8,2  4=E,8,2  5=O,8,2 |

## Function Code Addressing

### Register Address Formula:
```
Register Address = (Group * 256) + Parameter

Example: P14.01 → (0x14 * 256) + 0x01 = 0x1401
```

### Examples:
- P00.01 → 0x0001
- P00.02 → 0x0002
- P14.00 → 0x1400
- P14.01 → 0x1401
- P14.02 → 0x1402

## Control Example (Python)

```python
import serial
import struct

def crc16(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return struct.pack('<H', crc)

def write_register(ser, slave, register, value):
    request = bytes([
        slave,
        0x06,
        (register >> 8) & 0xFF,
        register & 0xFF,
        (value >> 8) & 0xFF,
        value & 0xFF
    ])
    request += crc16(request)
    ser.write(request)
    return ser.read(8)

# Open serial port
ser = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=19200,
    parity=serial.PARITY_EVEN,
    timeout=1.0
)

# Set frequency to 20.00 Hz (send 2000 = 0x07D0)
write_register(ser, 1, 0x2001, 2000)

# Start forward
write_register(ser, 1, 0x2000, 0x0001)

# Stop
write_register(ser, 1, 0x2000, 0x0005)
```

## Troubleshooting

### No Response from VFD
1. Check RS485 wiring (A-A, B-B, GND-GND)
2. Verify VFD power is ON
3. Confirm slave address: P14.00 = 1
4. Confirm baud rate: P14.01 = 4 (19200)
5. Confirm parity: P14.02 = 1 (Even, 8, 1)
6. Check termination resistors (120Ω both ends)

### VFD Won't Start via Modbus
1. Check P00.01 = 2 (Communication control)
2. Check P00.02 = 0 (Modbus channel)
3. Verify no faults: Read register 0x2102 (should be 0x0000)
4. Check State Word 2 for "Ready to run" bit

### Communication Works But Motor Won't Run
1. Ensure motor is properly connected
2. Check for fault codes (register 0x2102)
3. Verify P00.01 = 2 and P00.02 = 0
4. Run motor autotuning if first use (P00.15)
5. Check motor parameters are configured

## Key Differences from CFW300

| Feature | CFW300 | GALT G540 |
|---------|--------|-----------|
| Register formula | P001 = register 1 | P00.01 = register 0x0001 |
| Default baud | Varies | 19200 |
| Default parity | Even | Even |
| Control address | 0x0000 (write only) | 0x2000 (read/write) |
| Freq address | 0x0001 | 0x2001 |
| Identification | None | 0x2103 = 0x01A1 |

## Manual Reference

See `galt_g500manual.pdf`:
- **Page 218-220**: P14 group (communication parameters)
- **Page 309-325**: Chapter 9 (Modbus protocol)
- **Page 320**: Control command addresses
- **Page 321-322**: Monitoring addresses

## Success Indicators

✓ Identification reads 0x01A1  
✓ Configuration parameters readable  
✓ State word 1 shows "Stopped" when idle  
✓ State word 2 shows control source  
✓ Bus voltage shows ~300V DC  
✓ Frequency settings take effect  
✓ Motor responds to start/stop commands  
