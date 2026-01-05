#!/usr/bin/env python3
"""
MCP2515 Direct SPI Test
Tests the CAN Controller on the Waveshare HAT (B) (usually CE0).
"""
import spidev
import time

def test_mcp2515(bus, device):
    print(f"Testing MCP2515 on SPI {bus}.{device}...")
    try:
        spi = spidev.SpiDev()
        spi.open(bus, device)
        spi.max_speed_hz = 100000
        spi.mode = 0

        # MCP2515 Commands
        RESET = 0xC0
        READ_STATUS = 0xA0
        RX_STATUS = 0xB0
        
        # 1. Send Reset
        print("  Sending RESET command...")
        spi.writebytes([RESET])
        time.sleep(0.1)
        
        # 2. Read Status
        # Expect non-zero status usually
        resp = spi.xfer2([READ_STATUS, 0x00])
        status = resp[1]
        print(f"  Status Register: 0x{status:02X}")
        
        if status == 0x00 or status == 0xFF:
             print("  ⚠️  Warning: Status is 0x00 or 0xFF (Suspicious)")
        else:
             print("  ✓ SUCCESS: MCP2515 is alive!")
             return True

        # 3. Read CNF1 Register (Address 0x2A) - Default is usually 0x00, let's try CANCTRL (0x0F)
        # Read Command: 0x03
        READ = 0x03
        CANCTRL = 0x0F
        
        resp = spi.xfer2([READ, CANCTRL, 0x00])
        val = resp[2]
        print(f"  CANCTRL Register: 0x{val:02X}")
        
        # Default for CANCTRL is 0x87 (Configuration Mode) upon Reset
        if val == 0x87:
            print("  ✓ SUCCESS: Read expected default value 0x87!")
            return True
        else:
            print(f"  ✗ FAILURE: Expected 0x87, got 0x{val:02X}")
            return False

    except Exception as e:
        print(f"  ERROR: {e}")
        return False
    finally:
        spi.close()

print("=" * 60)
print("MCP2515 SPI TEST")
print("=" * 60)

# Test CE0 (Standard for CAN on this HAT)
test_mcp2515(0, 0)

print("=" * 60)
