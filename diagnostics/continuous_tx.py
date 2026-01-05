#!/usr/bin/env python3
"""
Send continuous Modbus frames for multimeter testing
"""
import serial
import time
import struct

def calculate_crc(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return struct.pack('<H', crc)

port = '/dev/ttyUSB0'
ser = serial.Serial(port, 19200, bytesize=8, parity='E', stopbits=1, timeout=0.5)

print("="*70)
print("SENDING CONTINUOUS MODBUS FRAMES")
print("Measure voltage between VFD terminals 25 (A) and 26 (B)")
print("You should see voltage swinging during transmission")
print("Press Ctrl+C to stop")
print("="*70)

request = bytearray([0x01, 0x03, 0x00, 0x01, 0x00, 0x01])
request += calculate_crc(request)

try:
    count = 0
    while True:
        ser.write(request)
        count += 1
        if count % 10 == 0:
            print(f"Sent {count} frames...")
        time.sleep(0.2)  # Send every 200ms
except KeyboardInterrupt:
    print(f"\nStopped. Sent {count} total frames")
finally:
    ser.close()
