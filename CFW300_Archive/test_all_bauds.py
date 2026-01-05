#!/usr/bin/env python3
import serial
import time

PORT = "/dev/ttyUSB0"

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

# All possible baud rates
BAUD_RATES = [9600, 19200, 38400, 57600, 115200]

print("Testing all baud rates to see if P316 increments")
print("=" * 60)
print("Check P316 on VFD display after each test")
print()

for baud in BAUD_RATES:
    print(f"\nTesting {baud} baud...")
    
    ser = serial.Serial(port=PORT, baudrate=baud, bytesize=8, parity='E', stopbits=1, timeout=0.5)
    ser.rts = True
    ser.dtr = True
    
    # Send 10 simple read requests
    for i in range(10):
        # Read P001 (register 0)
        packet = bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x01])
        crc = calculate_crc(packet)
        packet += bytes([crc & 0xFF, (crc >> 8) & 0xFF])
        
        ser.write(packet)
        time.sleep(0.1)
        ser.read(100)  # Clear any response
    
    ser.close()
    
    print(f"  Sent 10 frames at {baud} baud.")
    time.sleep(1)

print("\nDone! Check P316 on VFD now.")
