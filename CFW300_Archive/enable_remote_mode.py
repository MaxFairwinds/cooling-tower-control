#!/usr/bin/env python3
"""
Send LOC/REM command via Modbus to switch VFD to REMOTE mode
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
print("SENDING REMOTE MODE COMMAND")
print("="*70)

# Write P682 = 0x0010 (bit 4 = 1 for REMOTE mode)
# P682 is register 682
request = bytearray([
    0x01,  # Slave address
    0x06,  # Function: Write Single Register
    0x02, 0xAA,  # Register 682 (0x02AA)
    0x00, 0x10   # Value: 0x0010 (bit 4 = REMOTE)
])
request += calculate_crc(request)

print(f"\nWriting P682 = 0x0010 (Enable REMOTE mode)")
print(f"TX: {request.hex(' ')}")

ser.reset_input_buffer()
ser.reset_output_buffer()
ser.write(request)
time.sleep(0.2)

response = ser.read(100)
print(f"RX: {response.hex(' ') if response else 'No response'}")

if len(response) >= 8:
    print("\n*** SUCCESS! VFD should now be in REMOTE mode ***")
    print("Try pressing the HMI run button - it should NOT work now")
else:
    print("\nNo valid response - VFD still not responding to Modbus")

ser.close()
