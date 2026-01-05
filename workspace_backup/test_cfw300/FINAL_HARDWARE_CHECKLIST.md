# CFW300 Final Hardware Checklist

## Status After Factory Reset
❌ Still no communication after factory reset and reconfiguration

## Critical Hardware Items to Check

### 1. **Waveshare RS485 HAT - Termination Jumper** ⚠️
The Waveshare RS485/CAN HAT has an onboard 120Ω termination resistor that can be enabled/disabled via jumper.

**For a simple 2-device setup (Pi ↔ CFW300):**
- ✅ **ENABLE** the 120Ω termination jumper on the Waveshare HAT
- Look for a jumper labeled "120Ω" or "TERM" near the RS485 terminals
- The jumper should be **CLOSED** (jumper cap installed)

**Why this matters:**
- RS485 requires termination resistors at BOTH ends of the bus
- CFW300 likely has internal termination
- Pi HAT needs termination enabled for proper signal integrity

### 2. **Physical Wiring Verification**

**Check these connections:**

**On Waveshare HAT:**
- A+ terminal → Wire to CFW300 RS485+
- B- terminal → Wire to CFW300 RS485-

**On CFW300:**
- Verify terminals are labeled RS485+ and RS485- (or A+/B-)
- NOT connected to analog inputs or other ports
- Terminals are tight (use screwdriver to verify)

**Wire Continuity Test:**
- Use multimeter in continuity mode
- Test: HAT A+ terminal to CFW300 RS485+ terminal
- Test: HAT B- terminal to CFW300 RS485- terminal
- Should beep/show continuity

### 3. **CFW300 Display Check**

When P220 and P221 are set to 5 (Serial), the CFW300 display should show:
- "Ser" indicator or serial mode indication
- If display shows "LOC" (Local) or "HMI", serial mode is NOT active

**If display doesn't show serial mode:**
- Power cycle the CFW300 (OFF, wait 10s, ON)
- Re-verify P220=5 and P221=5

### 4. **Ground/Common Connection**

Some RS485 setups require a common ground reference:
- Try connecting Pi GND to CFW300 GND/COM terminal
- This can help with signal integrity

### 5. **Test with Minimal Setup**

**Disconnect everything except:**
- Power to CFW300
- RS485 A+ and B- wires
- No motor connected
- No other sensors/devices

This eliminates interference from other equipment.

## Quick Verification Commands

### Check HAT is accessible:
```bash
ssh max@coolingtower.local
ls -l /dev/ttyS0
```

### Run test:
```bash
cd test_cfw300
source ../venv/bin/activate
python3 quick_test.py
```

### Run comprehensive scan:
```bash
python3 comprehensive_diagnostic.py
```

## If Still No Response

At this point, if there's still no response, the issue is one of:

1. **Termination jumper** - Most likely if not checked yet
2. **Wrong CFW300 terminals** - Double-check RS485+/RS485-
3. **Faulty wire** - Try different wires
4. **Waveshare HAT issue** - Try loopback test (connect A+ to B-)
5. **CFW300 RS485 port issue** - Rare, but possible hardware fault

## Loopback Test for Waveshare HAT

To verify the HAT is working:
1. Disconnect CFW300
2. On the HAT, connect A+ to B- with a jumper wire
3. Run a loopback test script (can create if needed)
4. This verifies the Pi can send/receive on RS485

## Next Steps

1. ✅ Check termination jumper on Waveshare HAT
2. ✅ Verify wiring with continuity test
3. ✅ Check CFW300 display shows "Ser" mode
4. ✅ Try adding GND connection
5. ✅ Power cycle CFW300
6. ✅ Run test again
