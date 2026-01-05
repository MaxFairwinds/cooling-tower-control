# CFW300 Troubleshooting Summary

## Current Status: NO COMMUNICATION

Despite extensive troubleshooting, the CFW300 VFD is not responding to Modbus commands.

## What We've Verified ✅

### Software Configuration
- ✅ **UART Enabled**: `/dev/ttyAMA0` (stable PL011 UART)
- ✅ **Python/PyModbus**: Version 3.11.3, correct API (`device_id`)
- ✅ **Serial Port**: `/dev/ttyAMA0` accessible, no conflicts
- ✅ **Baud Rates Tested**: 9600, 19200, 38400, 57600
- ✅ **Device IDs Tested**: 1, 100, 101, 102, 103, 247

### CFW300 Parameters
- ✅ **P220 = 6** (Serial/USB Remote)
- ✅ **P221 = 9** (Serial/USB Speed Reference)
- ✅ **P308 = 100** (Modbus Address)
- ✅ **P310 = 0** (9600 baud)
- ✅ **P311 = 0** (8N1 - No parity)
- ✅ **P312 = 2** (Modbus RTU Slave)
- ✅ **Factory Reset Performed**
- ✅ **Power Cycled Multiple Times**

### Hardware Configuration
- ✅ **CFW300-CRS485 Module**: Installed and verified
- ✅ **Termination**: Enabled on both HAT and CRS485 (S1.1/S1.2 ON)
- ✅ **Wiring Tested**: Both Normal (A->A, B->B) and Reversed (A->B, B->A)
- ✅ **Ground Connected**: Common ground between Pi and VFD
- ✅ **Register**: Using P680 (Status Word), not P683 (Speed Ref)

## Next Steps: Hardware Verification

Since all software and configuration is verified correct, the issue is likely **hardware-related**.

### 1. Waveshare HAT Loopback Test

**Test if the Waveshare HAT can transmit/receive at all:**

1. **Disconnect** the CFW300 wires from the Waveshare HAT
2. **Short** terminals A and B together on the HAT (loopback)
3. Run this test:

```python
from pymodbus.client import ModbusSerialClient
client = ModbusSerialClient(port="/dev/ttyAMA0", baudrate=9600, timeout=1)
client.connect()
result = client.read_holding_registers(0, count=1, device_id=1)
print(result)  # Should show an error but prove TX/RX works
client.close()
```

**Expected**: You should see data being transmitted and received (even if it's garbage).
**If this fails**: The Waveshare HAT is defective.

### 2. Check CFW300 CRS485 Module LEDs

Does the CFW300-CRS485 module have any status LEDs?
- **TX LED**: Should blink when Pi sends data
- **RX LED**: Should blink when receiving

**If no LEDs blink**: Module may be defective or not properly seated.

### 3. Try a Different RS-485 Device

If you have access to another Modbus RTU device (even a cheap USB-to-RS485 adapter on another computer), try connecting to the CFW300 to verify the VFD side is working.

### 4. Multimeter Voltage Check

With the Pi sending commands, use a multimeter to check:
- **Voltage between A and B**: Should fluctuate (differential signal)
- **If voltage is constant**: HAT is not transmitting

## Possible Hardware Failures

1. **Waveshare HAT**: Transceiver chip (SP3485) may be damaged
2. **CFW300-CRS485 Module**: May be defective or improperly installed
3. **Wiring**: Cable may have internal break (check continuity)
4. **Pi UART**: Less likely, but GPIO14/15 could be damaged

## Contact Information

If hardware is confirmed working, contact:
- **WEG Support**: For CFW300-CRS485 module issues
- **Waveshare Support**: For RS485 CAN HAT issues
