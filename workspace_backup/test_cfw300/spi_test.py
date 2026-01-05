#!/usr/bin/env python3
"""
Direct SPI Test for SC16IS752
Attempts to read/write the Scratchpad Register (SPR) to verify communication.
Bypasses the kernel driver to test hardware connection directly.
"""
import spidev
import time

def test_channel(bus, device, name):
    print(f"Testing {name} (SPI bus {bus}, device {device})...")
    try:
        spi = spidev.SpiDev()
        spi.open(bus, device)
        spi.max_speed_hz = 10000
        spi.mode = 0

        # SC16IS752 Register 7 is SPR (Scratchpad Register)
        # Read command: R/W=1, A3-A0=0111, 000 -> 1011 1000 -> 0xB8
        READ_SPR = 0xB8
        # Write command: R/W=0, A3-A0=0111, 000 -> 0011 1000 -> 0x38
        WRITE_SPR = 0x38
        
        TEST_VAL = 0xAA

        # Write 0xAA to SPR
        # [Command, Value]
        spi.xfer2([WRITE_SPR, TEST_VAL])
        
        # Read back
        # [Command, Dummy] -> returns [Dummy, Value]
        resp = spi.xfer2([READ_SPR, 0x00])
        read_val = resp[1]
        
        print(f"  Wrote: 0x{TEST_VAL:02X}")
        print(f"  Read:  0x{read_val:02X}")
        
        if read_val == TEST_VAL:
            print(f"  ✓ SUCCESS: {name} is responding!")
            spi.close()
            return True
        else:
            print(f"  ✗ FAILURE: {name} returned incorrect value.")
            
        # Try another value to be sure
        TEST_VAL_2 = 0x55
        spi.xfer2([WRITE_SPR, TEST_VAL_2])
        resp = spi.xfer2([READ_SPR, 0x00])
        read_val = resp[1]
        print(f"  Wrote: 0x{TEST_VAL_2:02X}")
        print(f"  Read:  0x{read_val:02X}")
        
        if read_val == TEST_VAL_2:
            print(f"  ✓ SUCCESS: {name} is responding!")
            spi.close()
            return True
            
        spi.close()
        return False
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

print("=" * 60)
print("SC16IS752 DIRECT SPI TEST")
print("=" * 60)
print()

# Test SPI0.0 (CE0) - Usually CAN
test_channel(0, 0, "SPI0.0 (CE0)")
print()

# Test SPI0.1 (CE1) - Usually RS485
test_channel(0, 1, "SPI0.1 (CE1)")
print()

print("=" * 60)
