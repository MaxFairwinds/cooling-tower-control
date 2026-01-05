#!/usr/bin/env python3
"""
Send multiple rapid Modbus requests - maybe VFD needs initialization
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
print("SENDING BURST OF MODBUS REQUESTS")
print("="*70)

# Send 20 rapid requests
for i in range(20):
    request = bytearray([0x01, 0x03, 0x00, 0x01, 0x00, 0x01])
    request += calculate_crc(request)
    
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    ser.write(request)
    time.sleep(0.15)
    
    response = ser.read(100)
    
    if len(response) >= 7:
        print(f"\n*** REQUEST {i+1}: SUCCESS! ***")
        print(f"Response: {response.hex(' ')}")
        break
    elif len(response) > 1:
        print(f"Request {i+1}: {len(response)} bytes: {response.hex(' ')}")
    elif i % 5 == 4:
        print(f"Request {i+1}: Still getting 1 byte")

print("\nChecking P316 status...")
time.sleep(0.5)

# Check P316
request = bytearray([0x01, 0x03, 0x01, 0x3C, 0x00, 0x01])
request += calculate_crc(request)
ser.write(request)
time.sleep(0.15)
response = ser.read(100)

if len(response) >= 7:
    value = (response[3] << 8) | response[4]
    print(f"P316 = {value}")
else:
    print(f"P316 read failed: {response.hex(' ') if response else 'no response'}")

ser.close()
