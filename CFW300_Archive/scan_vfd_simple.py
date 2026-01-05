#!/usr/bin/env python3
import serial
import time

PORT = "/dev/ttyUSB0"
BAUD = 19200

def calculate_crc(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

print("VFD Scanner - Looking for ANY response")
print("=" * 60)

ser = serial.Serial(port=PORT, baudrate=BAUD, bytesize=8, parity='E', stopbits=1, timeout=0.5)
ser.rts = True
ser.dtr = True

# Try reading first 20 registers
for reg in range(20):
    packet = bytes([0x01, 0x03, 0x00, reg, 0x00, 0x01])
    crc = calculate_crc(packet)
    packet += bytes([crc & 0xFF, (crc >> 8) & 0xFF])
    
    ser.reset_input_buffer()
    ser.write(packet)
    time.sleep(0.1)
    
    response = ser.read(100)
    if response:
        print(f"Register {reg:3d} (0x{reg:04X}): RESPONSE! {response.hex(' ')}")
    else:
        print(f"Register {reg:3d} (0x{reg:04X}): no response")

ser.close()
print("\nScan complete")
