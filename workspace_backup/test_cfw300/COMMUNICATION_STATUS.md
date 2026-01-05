# CFW300 Communication Troubleshooting Summary

## Current Status: ❌ NO COMMUNICATION

After extensive testing, the CFW300 is not responding to any Modbus commands.

## What We've Verified ✅

### Software & Configuration
- ✅ Raspberry Pi serial port `/dev/ttyS0` is working
- ✅ Python code executes without errors
- ✅ Pymodbus library is functioning correctly
- ✅ Correct device ID (100) configured in test scripts
- ✅ Correct baud rate (9600) configured
- ✅ Correct parity (None) configured

### CFW300 Parameters (User Confirmed)
- ✅ P220 = 5 (Serial command source)
- ✅ P221 = 5 (Serial speed reference)
- ✅ P308 = 100 (RS-485 address)
- ✅ P310 = 0 (9600 baud)

### Tests Performed
- ✅ Tested device IDs: 1, 100, 101, 102, 103, 247
- ✅ Tested baud rates: 9600, 19200, 38400
- ✅ Swapped A+/B- wiring polarity
- ✅ Scanned multiple registers

## Remaining Possibilities

Since all software and configuration is correct, the issue MUST be hardware-related:

### 1. **Wiring Issue** (Most Likely)
   - **Action**: Double-check physical connections
   - Verify continuity of wires with multimeter
   - Ensure terminals are tight on both Pi HAT and CFW300
   - Try swapping back to original polarity (A+ to A+, B- to B-)
   - Check if wires are connected to correct terminals on CFW300

### 2. **CFW300 Not Actually in Serial Mode**
   - **Action**: Power cycle the CFW300
   - After setting P220/P221 to 5, the CFW300 may need a reboot
   - Turn OFF CFW300, wait 10 seconds, turn back ON
   - Verify display shows "Ser" or serial indication

### 3. **Termination Resistor**
   - **Action**: Check if termination resistor is needed
   - Some RS-485 setups require 120Ω resistor
   - Waveshare HAT may have jumper for termination
   - CFW300 may have internal termination setting

### 4. **Wrong CFW300 Terminals**
   - **Action**: Verify using correct RS-485 terminals
   - CFW300 should have terminals labeled RS485+ and RS485-
   - Ensure not connected to analog inputs or other ports

### 5. **Ground/Common Issue**
   - **Action**: Try connecting ground between Pi and CFW300
   - Some RS-485 setups need common ground reference

## Recommended Next Steps

1. **Power cycle CFW300** (turn off, wait 10s, turn on)
2. **Verify wiring with multimeter** (continuity test)
3. **Check Waveshare HAT termination jumper**
4. **Try original wire polarity** (undo the swap)
5. **Verify CFW300 terminal labels** (RS485+ and RS485-)

## Quick Test Command

After making any changes, run:
```bash
ssh max@coolingtower.local
cd test_cfw300
source ../venv/bin/activate
python3 quick_test.py
```

## Need More Help?

If still no response after trying above:
1. Take photo of CFW300 wiring terminals
2. Take photo of Waveshare HAT connections
3. Check CFW300 manual for RS-485 terminal diagram
4. Verify CFW300 firmware supports Modbus RTU
