# CFW300 Health Check Guide

## 1. Basic VFD Operation Test (No Serial)

**Test if the CFW300 works at all:**

1. **Set to Local Mode**:
   - Press `P` button repeatedly until you see `P220`
   - Press `▲` or `▼` to set value to `0` (Local/HMI)
   - Press `P` to save

2. **Set Speed Reference**:
   - Press `P` until you see `P133` (HMI Speed Reference)
   - Set to `10.00` Hz (low speed for safety)
   - Press `P` to save

3. **Run the Motor**:
   - Press the **Green (RUN)** button on the keypad
   - **Expected**: VFD should start, display should show frequency ramping up
   - **If this works**: VFD hardware is OK

4. **Stop the Motor**:
   - Press the **Red (STOP)** button

**If the VFD runs in Local mode, the hardware is fine. The issue is definitely the serial communication.**

---

## 2. Check Serial Communication Status

**View serial communication diagnostics:**

1. **Check P680 (Status Word)**:
   - Press `P` until you see `P680`
   - Note the value (hexadecimal)
   - This shows VFD status bits

2. **Check P681 (Control Word)**:
   - Press `P` until you see `P681`
   - Should show `0000` if no serial commands received
   - **If it shows non-zero**: VFD IS receiving serial data!

3. **Check P314 (Serial Watchdog)**:
   - Press `P` until you see `P314`
   - If set to 0.0s, watchdog is disabled (good for testing)
   - If non-zero and you see "Ser Err" on display, communication timed out

---

## 3. Verify CRS485 Module Installation

**Physical check:**

1. **Power OFF the CFW300** (wait 10 minutes for discharge)
2. **Open the VFD cover**
3. **Check CRS485 module**:
   - Is it fully seated in the connector slot?
   - Are the terminals tight (A-, B+, GND)?
   - Any visible damage to the module?

4. **Check for LEDs on CRS485 module**:
   - Some modules have TX/RX LEDs
   - Power ON and watch for blinking when Pi sends data

---

## 4. Test with WEG Software (If Available)

**WEG provides free software for CFW300:**

1. **Download WEG SuperDrive G2** (free from WEG website)
2. **Connect via USB** (CFW300 has mini-USB on CRS485 module)
3. **Read parameters** from VFD
4. **If this works**: CRS485 module is functional, issue is RS-485 specific

---

## 5. Monitor Serial Activity (Advanced)

**Check if VFD is seeing ANY serial data:**

1. **Set P314 = 1.0** (1 second watchdog)
2. **Set P220 = 6, P221 = 9** (Serial mode)
3. **Run the Pi test script**
4. **Watch the CFW300 display**:
   - Does it show "Ser" or "COM" indicator?
   - Does it show "Ser Err" after 1 second?
   - **If "Ser Err" appears**: VFD expects serial but isn't receiving valid data

---

## 6. Parameter Readback Verification

**Verify parameters actually saved:**

Go through each parameter and verify:
- `P220` = `6` (not 5!)
- `P221` = `9` (not 5!)
- `P308` = `100`
- `P310` = `0`
- `P311` = `0`
- `P312` = `2`

**If any are wrong, the VFD may have rejected the setting or you may have set the wrong parameter.**

---

## 7. Check Error History

**View error log:**

1. Press `P` until you see `P050` (Last Alarm)
2. Check if there are any communication errors logged
3. Press `▲` to cycle through error history

---

## Interpretation

| Symptom | Likely Cause |
|---------|-------------|
| VFD won't run in Local mode | VFD hardware failure |
| VFD runs Local, but P681 = 0000 | No serial data reaching VFD |
| VFD runs Local, P681 shows data | VFD receiving but not responding (check P312) |
| "Ser Err" appears | VFD expects serial but data is invalid/corrupted |
| USB works but RS-485 doesn't | CRS485 RS-485 circuit issue |

---

## Next Steps Based on Results

**If VFD runs in Local mode:**
→ VFD is healthy. Issue is Waveshare HAT or wiring.

**If P681 shows non-zero:**
→ VFD IS receiving data! Check P312 and response registers.

**If "Ser Err" appears:**
→ Data is reaching VFD but is corrupted (baud rate mismatch, noise, etc.)

**If USB works:**
→ CRS485 module is partially functional. RS-485 transceiver may be damaged.
