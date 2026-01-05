#!/usr/bin/env python3
"""
Dual-Channel RS-485 Loopback Test
For Waveshare RS485 CAN HAT (B) which has two channels.

WIRING REQUIRED:
- Connect Channel 0 A  <-->  Channel 1 A
- Connect Channel 0 B  <-->  Channel 1 B
"""
import serial
import time

print("=" * 60)
print("DUAL-CHANNEL RS-485 LOOPBACK TEST")
print("=" * 60)
print()
print("INSTRUCTIONS:")
print("1. Connect Channel 0 'A' to Channel 1 'A'")
print("2. Connect Channel 0 'B' to Channel 1 'B'")
print()

try:
    # Open both ports
    port0 = serial.Serial("/dev/ttySC0", baudrate=9600, timeout=1)
    port1 = serial.Serial("/dev/ttySC1", baudrate=9600, timeout=1)
    
    print(f"Opened {port0.port} and {port1.port}")
    print()

    # Test 1: Port 0 -> Port 1
    msg1 = b"HELLO_FROM_0"
    print(f"Sending from {port0.port}: {msg1}")
    port0.write(msg1)
    port0.flush()
    time.sleep(0.1)
    
    recv1 = port1.read(len(msg1))
    print(f"Received on {port1.port}:  {recv1}")
    
    if msg1 == recv1:
        print("✓ PASS: Port 0 -> Port 1")
    else:
        print("✗ FAIL: Port 0 -> Port 1")
    print()

    # Test 2: Port 1 -> Port 0
    msg2 = b"HELLO_FROM_1"
    print(f"Sending from {port1.port}: {msg2}")
    port1.write(msg2)
    port1.flush()
    time.sleep(0.1)
    
    recv2 = port0.read(len(msg2))
    print(f"Received on {port0.port}:  {recv2}")
    
    if msg2 == recv2:
        print("✓ PASS: Port 1 -> Port 0")
    else:
        print("✗ FAIL: Port 1 -> Port 0")

    port0.close()
    port1.close()

except Exception as e:
    print(f"\nERROR: {e}")
    print("Check if /dev/ttySC0 and /dev/ttySC1 exist.")

print()
print("=" * 60)
