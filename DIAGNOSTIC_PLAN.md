# CFW300 Communication Diagnostic Plan

## Current Status
- ✅ VFD parameters set correctly (P220=6, P221=9, P310=1, P311=1, P312=2)
- ✅ Python script sends Modbus request
- ✅ Adapter TXD LED blinks (transmitting)
- ❌ **P316 = 0 (Inactive) - VFD NOT detecting ANY serial communication**
- ❌ RXD LED never blinks (no response)
- ❌ Script returns "0 bytes: NONE"

## Root Cause Analysis

P316 = 0 means one of these:
1. **Adapter not transmitting valid RS485 signals** (voltage/timing issues)
2. **Wiring polarity reversed** (A/B swapped or miswired)
3. **VFD RS485 module not powered/enabled**
4. **Electrical incompatibility** (voltage levels, termination)

---

## Test Plan (Systematic Isolation)

### TEST 1: Verify Adapter Output with Multimeter
**Goal**: Confirm adapter is generating differential voltage on A/B

**Procedure**:
1. Disconnect VFD wires from adapter
2. Run `quick_test.py` on Pi
3. Measure with multimeter (DC volts):
   - Between A and B terminals: Should see ~2-3V differential when transmitting
   - Between A and GND: Should see voltage
   - Between B and GND: Should see opposite polarity voltage

**Expected**: Clear voltage swing during transmission
**If fails**: Adapter hardware issue

---

### TEST 2: Check Wiring Polarity
**Goal**: Verify A goes to A, B goes to B

**Current wiring** (verify):
```
Waveshare Adapter        CFW300 VFD
    A+    ------------>   A  (Terminal ?)
    B-    ------------>   B  (Terminal ?)
   GND    ------------>   GND (Terminal ?)
```

**Things to verify**:
- What terminal numbers are you using on the CFW300?
- Does the CFW300 have an RS485 accessory module installed?
- Are the terminals labeled clearly?

**Critical Note from Manual**: Some adapters use opposite A/B conventions!

---

### TEST 3: CFW300 RS485 Module Check
**Goal**: Verify RS485 hardware is present and functional

**Questions to answer**:
1. Does your CFW300 have a **CRS485 communication module** installed?
   - Look for an accessory card plugged into the VFD
   - Should have terminals labeled for RS485
   
2. Does the CRS485 module have LEDs?
   - Some modules have TX/RX indicator LEDs
   - Do they blink when you send data?

3. Can you access the VFD via **USB**?
   - CFW300 CRS485 module usually has mini-USB port
   - If USB works but RS485 doesn't → RS485 transceiver problem

---

### TEST 4: Measure Signal at VFD Terminals
**Goal**: Confirm signals are reaching the VFD

**Procedure**:
1. Keep wires connected to VFD
2. Run `quick_test.py`
3. Measure at **VFD terminals** (not adapter):
   - Voltage between A and B during transmission
   - Should see differential signal

**Expected**: Same 2-3V differential seen at adapter
**If fails**: Wiring issue (break, bad connection, wrong terminals)

---

### TEST 5: Capture Raw Bytes Being Sent
**Goal**: Verify correct Modbus packet format

**Create diagnostic script**:
