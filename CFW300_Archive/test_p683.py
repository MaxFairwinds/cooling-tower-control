#!/usr/bin/env python3
"""
Test reading P683 (Status Word) - a register that should always respond
"""
import serial
import time

PORT = "/dev/ttyUSB0"
BAUD = 19200
VFD_ADDR = 1

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

print("Testing P683 (Status Word) - Should always respond")
print("=" * 60)

ser = serial.Serial(port=PORT, baudrate=BAUD, bytesize=8, parity='E', stopbits=1, timeout=0.5)
ser.rts = True
ser.dtr = True

# Try reading P683 (register 683)
packet = bytes([VFD_ADDR, 0x03, 0x02, 0xAB, 0x00, 0x01])  # Read 683 (0x02AB)
crc = calculate_crc(packet)
packet += bytes([crc & 0xFF, (crc >> 8) & 0xFF])

print(f"Reading P683 (register 683 = 0x02AB)")
print(f"TX: {packet.hex(' ')}")

ser.reset_input_buffer()
ser.write(packet)
time.sleep(0.2)

response = ser.read(100)
print(f"RX: {response.hex(' ') if response else 'NOTHING'}")
print()

if response:
    print("✓ VFD RESPONDED!")
    print(f"Response length: {len(response)} bytes")
else:
    print("✗ No response")
    print("\nNow check P316 on VFD display - did it increment?")

ser.close()
