#!/usr/bin/env python3
"""
RS-485 FLOOD TEST
Sends continuous data to saturate the TX line.
This makes it much easier to see voltage changes on a multimeter.
"""
import serial
import time

print("=" * 60)
print("RS-485 FLOOD TEST")
print("=" * 60)
print()
print("This script will send continuous data (0x55) to the UART.")
print("This creates a 50% duty cycle square wave.")
print()
print("INSTRUCTIONS:")
print("1. Measure voltage between A and B.")
print("2. It should be STEADY when script is NOT running.")
print("3. It should CHANGE/FLUCTUATE when script IS running.")
print()

# Open serial port
ser = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=1)

print(f"Flooding {ser.port} at {ser.baudrate} baud...")
print("Press Ctrl+C to stop.")
print()

try:
    while True:
        # Send 100 bytes of 0x55 (01010101 pattern)
        # This keeps the line busy for ~100ms
        ser.write(b'\x55' * 100)
        # No sleep - keep it saturated
        
except KeyboardInterrupt:
    print("\nStopped.")
    ser.close()
