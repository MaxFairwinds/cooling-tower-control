#!/usr/bin/env python3
"""
Continuous MCP2515 SPI Test Loop
Runs indefinitely to help diagnose intermittent connection issues.
"""
import spidev
import time
import sys

def test_once():
    try:
        spi = spidev.SpiDev()
        spi.open(0, 0)
        spi.max_speed_hz = 100000
        spi.mode = 0

        # Read CANCTRL (0x0F) - Default 0x87
        READ = 0x03
        CANCTRL = 0x0F
        
        resp = spi.xfer2([READ, CANCTRL, 0x00])
        val = resp[2]
        spi.close()
        
        return val
    except:
        return None

print("=" * 60)
print("CONTINUOUS SPI TEST (Press Ctrl+C to stop)")
print("=" * 60)
print("Please PRESS DOWN on the HAT or WIGGLE it gently.")
print("Looking for value 0x87...")
print()

try:
    while True:
        val = test_once()
        if val == 0x87:
            print(f"✓ SUCCESS! Read 0x{val:02X} (Connection Good!)")
        elif val is None:
            print("✗ ERROR: SPI Open Failed")
        elif val == 0x00:
            print(f"✗ FAIL: Read 0x{val:02X} (No Response)")
        else:
            print(f"? WEIRD: Read 0x{val:02X} (Garbage?)")
            
        time.sleep(0.5)
        
except KeyboardInterrupt:
    print("\nStopped.")
