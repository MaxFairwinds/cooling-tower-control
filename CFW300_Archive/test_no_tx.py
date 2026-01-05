#!/usr/bin/env python3
import serial
import time

print("Testing receive without transmit...")
print("=" * 60)

ser = serial.Serial("/dev/ttyUSB0", 19200, parity="E", stopbits=1, bytesize=8, timeout=1)
ser.rts = True
ser.dtr = True
time.sleep(0.5)

ser.reset_input_buffer()
# Do NOT send anything
time.sleep(0.5)

response = ser.read(100)
print(f"No TX - RX: {response.hex() if response else 'NONE'} ({len(response)} bytes)")

ser.close()
