#!/usr/bin/env python3
"""
RS-485 Loopback Test
This will definitively prove if the Waveshare HAT can transmit.

SETUP: Short terminals A and B together with a wire (loopback)
"""
import fcntl
import struct
import serial
import time

# RS-485 ioctl constants
TIOCSRS485 = 0x542F
SER_RS485_ENABLED = (1 << 0)
SER_RS485_RTS_ON_SEND = (1 << 1)

def enable_rs485(ser):
    """Enable RS-485 mode on the serial port."""
    flags = SER_RS485_ENABLED | SER_RS485_RTS_ON_SEND
    rs485_config = struct.pack('I' * 7, flags, 0, 0, 0, 0, 0, 0)
    fcntl.ioctl(ser.fileno(), TIOCSRS485, rs485_config)

print("=" * 60)
print("RS-485 LOOPBACK TEST")
print("=" * 60)
print()
print("IMPORTANT: Short A and B terminals together before running!")
print()
input("Press ENTER when A and B are shorted together...")
print()

# Open serial port
ser = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=1)

# Enable RS-485 mode
print("Enabling RS-485 mode...")
enable_rs485(ser)
print("✓ RS-485 mode enabled")
print()

# Test transmission and reception
test_message = b"HELLO"
print(f"Sending: {test_message}")
ser.write(test_message)
ser.flush()

time.sleep(0.1)

# Try to read back
received = ser.read(len(test_message))
print(f"Received: {received}")
print()

if received == test_message:
    print("✓✓✓ SUCCESS! Waveshare HAT is working!")
    print("    The HAT can transmit and receive.")
    print("    The problem is elsewhere (wiring, CFW300, etc.)")
else:
    print("✗✗✗ FAILURE! Waveshare HAT is NOT working!")
    print(f"    Expected: {test_message}")
    print(f"    Got: {received}")
    print("    The HAT is defective or not configured correctly.")

print()
print("=" * 60)

ser.close()
