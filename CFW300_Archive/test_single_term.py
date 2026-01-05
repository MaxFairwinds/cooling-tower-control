#!/usr/bin/env python3
import serial
import time

ser = serial.Serial("/dev/ttyUSB0", 19200, parity="E", timeout=1)
time.sleep(0.2)

# Read P001
packet = bytes([0x01, 0x03, 0x00, 0x01, 0x00, 0x01, 0xD5, 0xCA])

print("Testing with VFD termination OFF...")
for i in range(3):
    ser.reset_input_buffer()
    ser.write(packet)
    time.sleep(0.3)
    r = ser.read(100)
    print(f"Attempt {i+1}: RX={r.hex() if r else 'NONE'} ({len(r)} bytes)")

ser.close()
