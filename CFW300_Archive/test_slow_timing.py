#!/usr/bin/env python3
import serial
import time

# Open serial port with aggressive settings
ser = serial.Serial("/dev/ttyUSB0", 19200, parity="E", stopbits=1, bytesize=8, timeout=2)
ser.rts = True
ser.dtr = True
time.sleep(0.5)

print("Testing with slower timing and longer timeout...")
print("=" * 60)

# Read P001
packet = bytes([0x01, 0x03, 0x00, 0x01, 0x00, 0x01, 0xD5, 0xCA])

ser.reset_input_buffer()
ser.write(packet)
print(f"TX: {packet.hex()}")

# Wait longer and read byte by byte
time.sleep(1.0)
response = ser.read(100)

print(f"RX: {response.hex() if response else 'NONE'}")
print(f"Length: {len(response)} bytes")

if response:
    print(f"Bytes: {' '.join(f'{b:02x} ({b})' for b in response)}")

ser.close()
