# CFW300 Connection Troubleshooting

## Test Results

**Status**: ❌ No response from CFW300

**What Worked:**
- ✅ Serial port `/dev/ttyS0` opens successfully
- ✅ Python code executes without errors
- ✅ Modbus library functioning

**What Failed:**
- ❌ No response from CFW300 at device IDs: 1, 101, 102, 103, 247
- ❌ All Modbus register reads timeout after 3 retries

## Root Cause

The CFW300 is either:
1. Not configured for Modbus communication
2. Using a different device ID or baud rate
3. RS-485 wiring issue (polarity or connection)

## Troubleshooting Steps

### 1. Check CFW300 Parameters (CRITICAL)

Use the CFW300 keypad to verify these parameters:

| Parameter | Required Value | Description |
|-----------|----------------|-------------|
| **P220** | **5** | Command source = Serial |
| **P221** | **5** | Speed reference = Serial |
| **P308** | **1-247** | **RS-485 Address** (Set to 101) |
| **P310** | **0** | **Baud Rate** (0=9600) |
| **P311** | **0** | **Parity** (0=None) |
| **P313** | **1 or 2** | Comm timeout action |

> [!NOTE]
> **P300/P301 are for DC Braking** - do not change them!
> Use **P308** for Address and **P310** for Baud Rate.

**Most Common Issue**: P220 and P221 not set to Serial (5)

### 2. Verify RS-485 Wiring

**CRITICAL: Polarity Mismatch Issue**
- **Waveshare HAT**: Uses chip convention where **A is (+)** and **B is (-)**.
- **WEG CFW300**: Uses standard convention where **A is (-)** and **B is (+)**.

**You MUST connect:**
- **Waveshare A (+)** <---> **CFW300 B (+)**
- **Waveshare B (-)** <---> **CFW300 A (-)**

Do NOT connect "A to A" and "B to B" - this will be reversed!

### 3. Check Physical Connections

- ✓ CFW300 powered on?
- ✓ RS-485 terminals tight?
- ✓ Correct terminals on Waveshare HAT?
- ✓ Cable continuity?
- Disconnect wires and check continuity from Pi HAT terminals to CFW300 terminals.
- Ensure wires are tight and making good contact.

### 4. Connect Common Ground (CRITICAL)

RS-485 is differential but requires a common ground reference if the potential difference is too high.

**Connect a wire between:**
- **Raspberry Pi HAT GND**
- **CFW300 CRS485 Module Terminal 27 (GND)** or **29 (GND)**

This resolves "floating ground" issues which are very common with isolated power supplies.

### 5. Test with Different Device ID

If P300 is set to something other than 101, update `config_cfw300.py`:

```python
VFD_CONFIG = {
    'test_vfd_1': {
        'device_id': 1,  # Change this to match P300
        ...
    }
}
```

## Quick Tests

### Test 1: Check CFW300 Display
- Does CFW300 show "Ser" or "Serial" on display when P220/P221 = 5?
- Does it show communication errors?

### Test 2: Try Device ID 1
```bash
cd test_cfw300
source ../venv/bin/activate
python3 -c "
from vfd_controller_cfw300 import CFW300Manager
m = CFW300Manager('/dev/ttyS0', 9600, 60.0)
m.connect()
m.add_vfd('test', 1, 'Test')
print(m.get_vfd('test').read_register(683))
"
```

### Test 3: Swap A+/B- Wires
Physically swap the wires and run `quick_test.py` again.

## Next Steps

1. **Check P220 and P221** - Most likely issue
2. **Note the value of P300** - This is the device ID
3. **Try swapping A+/B-** - Polarity issue
4. **Run diagnostic.py again** after changes

## Need Help?

Run the diagnostic tool:
```bash
cd test_cfw300
source ../venv/bin/activate
python3 diagnostic.py
```

This will scan multiple device IDs automatically.
