#!/usr/bin/env python3
"""
Try different slave addresses including broadcast
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
ser = serial.Serial(port, 19200, bytesize=8, parity='E', stopbits=1, timeout=0.3)

print("="*70)
print("TRYING DIFFERENT SLAVE ADDRESSES")
print("="*70)

# Try addresses 1-10 and 247
addresses = list(range(1, 11)) + [247]

for addr in addresses:
    # Read P001
    request = bytearray([addr, 0x03, 0x00, 0x01, 0x00, 0x01])
    request += calculate_crc(request)
    
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    ser.write(request)
    time.sleep(0.1)
    
    response = ser.read(100)
    
    if len(response) >= 7:
        print(f"Address {addr}: SUCCESS! Response: {response.hex(' ')}")
        break
    elif len(response) > 0:
        print(f"Address {addr}: {len(response)} bytes: {response.hex(' ')}")
    else:
        print(f"Address {addr}: No response")

ser.close()
