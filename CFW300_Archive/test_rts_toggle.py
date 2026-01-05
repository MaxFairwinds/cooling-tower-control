#!/usr/bin/env python3
import serial
import time

# Open serial port
ser = serial.Serial("/dev/ttyUSB0", 19200, parity="E", stopbits=1, bytesize=8, timeout=3)

print("Testing with RTS toggle for TX/RX switching...")
print("=" * 60)

# Read P001
packet = bytes([0x01, 0x03, 0x00, 0x01, 0x00, 0x01, 0xD5, 0xCA])

ser.reset_input_buffer()

# Enable transmit
ser.rts = True
ser.dtr = True
time.sleep(0.01)

# Send
ser.write(packet)
print(f"TX: {packet.hex()}")
time.sleep(0.01)

# Switch to receive mode
ser.rts = False
ser.dtr = False
time.sleep(0.5)

# Read response
response = ser.read(100)

print(f"RX: {response.hex() if response else 'NONE'}")
print(f"Length: {len(response)} bytes")

if response:
    print(f"Bytes: {' '.join(f'{b:02x}' for b in response)}")

ser.close()
