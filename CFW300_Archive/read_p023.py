#!/usr/bin/env python3
"""Read P023 (firmware version) from VFD via HMI"""
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

def read_param(ser, param_num):
    request = bytearray([0x01, 0x03, (param_num >> 8) & 0xFF, param_num & 0xFF, 0x00, 0x01])
    request += calculate_crc(request)
    
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    ser.write(request)
    time.sleep(0.1)
    
    response = ser.read(100)
    if len(response) >= 7 and response[0] == 0x01 and response[1] == 0x03:
        return (response[3] << 8) | response[4]
    return None

port = '/dev/ttyUSB0'
ser = serial.Serial(port, 19200, bytesize=8, parity='E', stopbits=1, timeout=0.5)

print("Reading VFD firmware version...")
p023 = read_param(ser, 23)

if p023:
    major = p023 // 100
    minor = p023 % 100
    print(f"P023 = {p023} ({major}.{minor:02d})")
else:
    print("P023: No response - read it manually from HMI")

ser.close()
