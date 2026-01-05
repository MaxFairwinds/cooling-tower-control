#!/usr/bin/env python3
"""
Test VFD pass-through: 
- Connect Adapter 1 to VFD (A-A, B-B)
- Keep Adapter 2 connected to Adapter 1 in parallel (VFD in the middle)
- Adapter 1 transmits, Adapter 2 receives
- This tests if VFD terminals pass signals through
"""
import serial
import time
import os

print("VFD Pass-Through Test")
print("=" * 60)
print("Wiring:")
print("  Adapter 1 → VFD terminals (A-A, B-B)")
print("  VFD should NOT interfere with signal")
print("  Can Adapter 2 still receive?")
print()

devices = [f"/dev/{d}" for d in os.listdir("/dev") if d.startswith("ttyUSB")]
devices.sort()

if len(devices) < 2:
    print(f"ERROR: Need 2 adapters")
    exit(1)

PORT1 = devices[0]
PORT2 = devices[1]

print(f"TX: {PORT1}")
print(f"RX: {PORT2}")
print()

ser1 = serial.Serial(port=PORT1, baudrate=19200, bytesize=8, parity='E', stopbits=1, timeout=0.5)
ser2 = serial.Serial(port=PORT2, baudrate=19200, bytesize=8, parity='E', stopbits=1, timeout=0.5)

ser1.rts = True
ser1.dtr = True

print("Testing with VFD in circuit...")
print()

success = 0
fail = 0

for i in range(10):
    test_msg = f"VFD{i:03d}".encode()
    
    ser1.reset_input_buffer()
    ser2.reset_input_buffer()
    
    ser1.write(test_msg)
    time.sleep(0.1)
    
    received = ser2.read(100)
    
    if received == test_msg:
        print(f"✓ Test {i+1}: SUCCESS - {test_msg.decode()}")
        success += 1
    else:
        print(f"✗ Test {i+1}: FAILED - TX={test_msg.decode()} RX={received.hex() if received else 'NOTHING'}")
        fail += 1
    
    time.sleep(0.1)

print()
print("=" * 60)
print(f"Results: {success} passed, {fail} failed")

if success == 10:
    print("✓ VFD terminals pass signal through correctly")
elif success > 0:
    print("⚠ Intermittent - possible VFD interference")
else:
    print("✗ VFD blocks or corrupts signal")

ser1.close()
ser2.close()
