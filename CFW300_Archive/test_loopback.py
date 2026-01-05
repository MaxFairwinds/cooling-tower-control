#!/usr/bin/env python3
"""
RS485 Loopback Test - Connect two Waveshare adapters together:
Adapter 1 A → Adapter 2 A
Adapter 1 B → Adapter 2 B
"""
import serial
import time
import sys

print("RS485 Loopback Test")
print("=" * 60)
print("Connect two USB-RS485 adapters:")
print("  Adapter 1 A → Adapter 2 A")
print("  Adapter 1 B → Adapter 2 B")
print()

# Find all USB serial devices
import os
devices = [f"/dev/{d}" for d in os.listdir("/dev") if d.startswith("ttyUSB")]
devices.sort()

if len(devices) < 2:
    print(f"ERROR: Found only {len(devices)} USB serial device(s)")
    print("Need 2 adapters connected!")
    sys.exit(1)

PORT1 = devices[0]
PORT2 = devices[1]

print(f"Using:")
print(f"  Transmit: {PORT1}")
print(f"  Receive:  {PORT2}")
print()

# Open both ports
ser1 = serial.Serial(port=PORT1, baudrate=19200, bytesize=8, parity='E', stopbits=1, timeout=1)
ser2 = serial.Serial(port=PORT2, baudrate=19200, bytesize=8, parity='E', stopbits=1, timeout=1)

ser1.rts = True
ser1.dtr = True
ser2.rts = True
ser2.dtr = True

print("Testing...")
print()

success_count = 0
fail_count = 0

for i in range(10):
    # Create test message
    test_msg = f"TEST{i:03d}".encode()
    
    # Clear buffers
    ser1.reset_input_buffer()
    ser2.reset_input_buffer()
    
    # Send from port 1
    ser1.write(test_msg)
    time.sleep(0.1)
    
    # Receive on port 2
    received = ser2.read(100)
    
    if received == test_msg:
        print(f"✓ Test {i+1}: TX={test_msg.decode()} RX={received.decode()} - SUCCESS")
        success_count += 1
    else:
        print(f"✗ Test {i+1}: TX={test_msg.decode()} RX={received.hex() if received else 'NOTHING'} - FAILED")
        fail_count += 1
    
    time.sleep(0.1)

print()
print("=" * 60)
print(f"Results: {success_count} passed, {fail_count} failed")

if success_count == 10:
    print("✓ Both adapters are working correctly!")
elif success_count > 0:
    print("⚠ Partial success - check connections")
else:
    print("✗ Complete failure - adapters or connections faulty")

ser1.close()
ser2.close()
