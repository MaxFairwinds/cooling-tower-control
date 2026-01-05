#!/usr/bin/env python3
"""Quick connection test for CFW300"""

from vfd_controller_cfw300 import CFW300Manager
import logging

logging.basicConfig(level=logging.INFO)

print("="*60)
print("CFW300 CONNECTION TEST")
print("="*60)

manager = CFW300Manager("/dev/ttyS0", 9600, 60.0)

if not manager.connect():
    print("ERROR: Failed to open serial port /dev/ttyS0")
    exit(1)

print("✓ Serial port opened successfully")

# Add VFD with device ID 100
manager.add_vfd("test", 100, "CFW300 Test Unit")
vfd = manager.get_vfd("test")

print("\nAttempting to read status word (P683)...")
status = vfd.read_register(683)

if status is not None:
    print(f"\n✓ SUCCESS! Communication working!")
    print(f"  Status word (P683): {status} (0x{status:04X})")
    
    # Try reading a few more registers
    print("\nReading additional registers...")
    freq = vfd.read_register(681)
    if freq is not None:
        print(f"  Speed reference (P681): {freq}")
    
    fault = vfd.read_register(48)
    if fault is not None:
        print(f"  Fault code (P048): {fault}")
    
else:
    print("\n✗ NO RESPONSE from CFW300")
    print("\nTroubleshooting:")
    print("  1. Check CFW300 device ID is set to 100 (P308)")
    print("  2. Check baud rate is 9600 (P310=0)")
    print("  3. Check parity is None (P311=0)")
    print("  4. Verify RS-485 wiring (A+ to A+, B- to B-)")
    print("     -> TRY SWAPPING A+ and B- WIRES (Polarity is often reversed)")
    print("  5. Check CFW300 is powered on")

manager.close()
print("\n" + "="*60)
