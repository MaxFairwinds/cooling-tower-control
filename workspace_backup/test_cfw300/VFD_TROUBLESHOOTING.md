# CFW300 VFD Connection Troubleshooting Guide

## Current Status
- ✓ USB-RS485 adapter detected at `/dev/ttyUSB0`
- ✓ Serial port opens successfully
- ✗ VFD not responding (timeout after 3 retries)

## Required VFD Parameter Checks

Please check these parameters on your CFW300 VFD display:

### P120 - Baud Rate
- **Expected:** 9600
- **Your Value:** _______
- **Options:** 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200

### P121 - Slave Address
- **Expected:** 1
- **Your Value:** _______
- **Range:** 1-247

### P122 - Parity
- **Expected:** 0 (None)
- **Your Value:** _______
- **Options:** 0=None, 1=Even, 2=Odd

## Wiring Verification

RS485 uses two wires (A and B). Verify your connections:

**USB-RS485 Adapter** → **CFW300 VFD**
- A+ (or D+) → Terminal 10 (A+)
- B- (or D-) → Terminal 11 (B-)
- GND (optional) → Terminal 12 (GND)

## Common Issues

1. **Wrong baud rate** - Most common issue
2. **Wrong slave ID** - VFD ignores messages not addressed to it
3. **Swapped A/B wires** - Communication fails completely
4. **VFD in local mode** - Some VFDs ignore Modbus when in local control
5. **Termination resistor** - Usually not needed for short cables

## Next Steps

Once you provide the P120, P121, P122 values, I can:
1. Update the test script to match your VFD settings
2. Create a parameter scanner to auto-detect settings
3. Test with different configurations
