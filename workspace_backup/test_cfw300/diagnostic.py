#!/usr/bin/env python3
"""
CFW300 Diagnostic Tool
Tests different device IDs and baud rates to help find configuration issues
"""

from vfd_controller_cfw300 import CFW300Manager
import time

print("="*60)
print("CFW300 DIAGNOSTIC TOOL")
print("="*60)
print("\nThis will test different device IDs and baud rates")
print("to help identify configuration issues.\n")

# Test different device IDs
device_ids_to_test = [1, 101, 102, 103, 247]  # Common IDs
baud_rates_to_test = [9600, 19200, 38400]  # Common baud rates

print("Testing Device IDs at 9600 baud...")
print("-" * 60)

manager = CFW300Manager("/dev/ttyS0", 9600, 60.0)
if not manager.connect():
    print("ERROR: Cannot open serial port")
    exit(1)

found = False

for device_id in device_ids_to_test:
    print(f"\nTrying Device ID {device_id}...", end=" ", flush=True)
    
    manager.add_vfd(f"test_{device_id}", device_id, f"Test ID {device_id}")
    vfd = manager.get_vfd(f"test_{device_id}")
    
    # Try to read status word
    status = vfd.read_register(683)
    
    if status is not None:
        print(f"✓ FOUND!")
        print(f"  Status word: {status} (0x{status:04X})")
        found = True
        break
    else:
        print("✗ No response")

manager.close()

if not found:
    print("\n" + "="*60)
    print("NO DEVICE FOUND at 9600 baud")
    print("\nNext steps:")
    print("1. Verify CFW300 is powered on")
    print("2. Check RS-485 wiring:")
    print("   - Pi A+ should connect to CFW300 RS485+")
    print("   - Pi B- should connect to CFW300 RS485-")
    print("3. Check CFW300 parameters:")
    print("   - P220 = 5 (Serial command source)")
    print("   - P221 = 5 (Serial speed reference)")
    print("   - P300 = Device ID (try 1 or 101)")
    print("   - P301 = 4 (9600 baud)")
    print("   - P302 = 0 (No parity)")
    print("4. Try swapping A+ and B- wires (polarity)")
    print("="*60)
else:
    print("\n" + "="*60)
    print("✓ CFW300 FOUND!")
    print(f"  Device ID: {device_id}")
    print(f"  Baud rate: 9600")
    print("\nUpdate config_cfw300.py with this device ID")
    print("="*60)
