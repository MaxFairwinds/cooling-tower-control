# CFW300 Test Environment

**Purpose**: Bench-top testing of RS-485 Modbus communication and control logic using WEG CFW300 VFD before connecting to production Galt G540 drives.

## Why Separate from Production?

- **Different register maps**: CFW300 uses P682/P681, G540 uses different addresses
- **Different device IDs**: Test uses 101-103, production uses 1-3
- **Safety**: Prevents accidental commands to production equipment
- **Clean testing**: Validate all functionality without touching live system

## Hardware Setup

### CFW300 Configuration Required

Configure these parameters on the CFW300 (via keypad or HMI):

| Parameter | Setting | Description |
|-----------|---------|-------------|
| **P220** | Serial | Command source = Modbus |
| **P221** | Serial | Speed reference source = Modbus |
| **P308** | 101 | RS-485 address (or 102, 103 for multi-unit) |
| **P310** | 0 | Baud rate = 9600 |
| **P311** | 0 | Parity = None |
| **P313** | 1 | Comm timeout = Stop motor |

### Wiring

```
Pi RS-485 HAT
    ├─ A+ ──── CFW300 RS-485 A+
    └─ B- ──── CFW300 RS-485 B-
```

Add 120Ω termination resistor if cable is long.

## Test Scripts

### 1. Automated Test Suite
```bash
python3 test_suite.py
```

**What it tests:**
- ✓ RS-485 connection
- ✓ Read/write registers
- ✓ Frequency scaling (Hz ↔ scaled value)
- ✓ Start/stop commands
- ✓ Error handling and timeouts

**Output**: PASS/FAIL for each test with summary

### 2. Interactive Test
```bash
python3 interactive_test.py
```

**Features:**
- Manual control menu
- Read status in real-time
- Set frequency
- Start/stop motor
- Frequency ramp test
- Read all registers

## What Can Be Tested Without a Motor

✅ **RS-485 Communication**
- Verify A/B polarity
- Confirm serial port works
- Test Modbus protocol

✅ **Register I/O**
- Read status registers
- Write frequency setpoint
- Read back values

✅ **Control Logic**
- Send start/stop commands
- Frequency scaling math
- Error handling

✅ **Safety Features**
- Communication timeout
- Retry logic
- Fault detection

## CFW300 vs G540 Differences

| Feature | CFW300 (Test) | G540 (Production) |
|---------|---------------|-------------------|
| **Device IDs** | 101-103 | 1-3 |
| **Control Word** | P682 | TBD (verify manual) |
| **Speed Ref** | P681 (scaled 0-8191) | TBD |
| **Status Word** | P683 | TBD |
| **Scaling** | 13-bit (0-8191) | TBD |

## Files in This Directory

```
test_cfw300/
├── config_cfw300.py           # CFW300-specific configuration
├── vfd_controller_cfw300.py   # CFW300 VFD controller
├── test_suite.py              # Automated test suite
├── interactive_test.py        # Manual control script
└── README_CFW300.md           # This file
```

## Expected Outcome

After successful testing:

1. ✅ Verified RS-485 hardware works
2. ✅ Confirmed Modbus communication
3. ✅ Validated frequency scaling
4. ✅ Tested control commands
5. ✅ Verified error handling
6. ✅ Ready to adapt code for G540 (just change register addresses)

## Next Steps

1. Run `test_suite.py` to validate all communication
2. Use `interactive_test.py` to explore manually
3. Test with motor connected (optional)
4. Document any issues or findings
5. When ready, adapt register addresses for G540 in production code

## Safety Notes

> [!WARNING]
> **Motor Will Start**
> 
> If a motor is connected to the CFW300, it will run during tests. Ensure:
> - Motor is properly secured
> - No load is connected
> - Emergency stop is accessible
> - You understand the test sequence

> [!IMPORTANT]
> **Production Isolation**
> 
> This test environment is completely separate from production G540 code. Device IDs 101-103 will never conflict with production IDs 1-3.
