#!/usr/bin/env python3
"""
CFW300 Deep Scan Tool
Scans a wide range of Device IDs and Baud Rates
"""

from vfd_controller_cfw300 import CFW300Manager
import time
import logging

# Enable pymodbus logging
logging.getLogger("pymodbus").setLevel(logging.DEBUG)
logging.getLogger("vfd_controller_cfw300").setLevel(logging.DEBUG)

print("="*60)
print("CFW300 DEEP SCAN TOOL")
print("="*60)

# Scan parameters
baud_rates = [9600, 19200, 38400]
device_ids = list(range(1, 11)) + list(range(100, 105)) + [247]

print(f"Scanning {len(device_ids)} IDs across {len(baud_rates)} baud rates...")
print("This may take a minute.\n")

found_any = False

for baud in baud_rates:
    print(f"Checking {baud} baud...")
    
    try:
        manager = CFW300Manager("/dev/ttyS0", baud, 60.0)
        if not manager.connect():
            print(f"  ERROR: Could not open serial port at {baud}")
            continue
            
        for device_id in device_ids:
            # print(f"  Probe ID {device_id}...", end="\r", flush=True)
            
            # Manually create client to avoid overhead
            manager.add_vfd(f"scan_{device_id}", device_id, "Scan")
            vfd = manager.get_vfd(f"scan_{device_id}")
            
            # Try to read status word (P683)
            # Use a short timeout/retry if possible, but pymodbus handles this
            status = vfd.read_register(683)
            
            if status is not None:
                print(f"  ✓ FOUND! Device ID: {device_id} at {baud} baud")
                print(f"    Status Word: {status} (0x{status:04X})")
                found_any = True
                
                # Try reading speed ref to confirm
                speed = vfd.read_register(681)
                if speed is not None:
                    print(f"    Speed Ref: {speed}")
                
        manager.close()
        
    except Exception as e:
        print(f"  Error at {baud} baud: {e}")

print("\n" + "="*60)
if found_any:
    print("SCAN COMPLETE - DEVICE FOUND!")
else:
    print("SCAN COMPLETE - NO DEVICES FOUND")
    print("\nTroubleshooting Tips:")
    print("1. Verify P220=5 and P221=5 (Serial)")
    print("2. Verify Wiring Polarity (Try swapping A+ and B-)")
    print("3. Verify Termination Resistor (Try adding/removing)")
print("="*60)
