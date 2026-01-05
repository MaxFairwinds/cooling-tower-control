#!/usr/bin/env python3
"""
Send Modbus and see if we get "00" byte even with VFD disconnected
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
print("TESTING WITH VFD - DISCONNECT VFD NOW IF YOU WANT TO TEST WITHOUT IT")
print("="*70)
print("Press Enter when ready...")
input()

request = bytearray([0x01, 0x03, 0x00, 0x01, 0x00, 0x01])
request += calculate_crc(request)

print(f"\nSending: {request.hex(' ')}")
ser.reset_input_buffer()
ser.reset_output_buffer()
ser.write(request)
time.sleep(0.15)

response = ser.read(100)
print(f"Received: {response.hex(' ') if response else 'Nothing'}")
print(f"Length: {len(response)} bytes")

ser.close()
