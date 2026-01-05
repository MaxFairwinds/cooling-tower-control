#!/usr/bin/env python3
"""
Ultra-simple raw serial loopback test.
No PyModbus, no RS-485 ioctl - just raw serial.
"""
import serial
import time

print("=" * 60)
print("RAW SERIAL LOOPBACK TEST (No RS-485 mode)")
print("=" * 60)
print()
print("Make sure A and B are shorted together!")
print()

# Open serial port with minimal configuration
ser = serial.Serial(
    port='/dev/ttyAMA0',
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1
)

print(f"Port: {ser.port}")
print(f"Baud: {ser.baudrate}")
print(f"Open: {ser.is_open}")
print()

# Clear any existing data
ser.reset_input_buffer()
ser.reset_output_buffer()

# Send simple bytes
test_data = b"TEST123"
print(f"Sending: {test_data}")
bytes_written = ser.write(test_data)
print(f"Wrote {bytes_written} bytes")
ser.flush()  # Wait for TX to complete

# Small delay
time.sleep(0.2)

# Try to read back
print(f"Bytes waiting: {ser.in_waiting}")
received = ser.read(len(test_data))
print(f"Received: {received}")
print()

if received == test_data:
    print("✓✓✓ SUCCESS! Serial TX and RX work!")
    print("    Problem is likely RS-485 transceiver or ioctl config")
elif len(received) > 0:
    print(f"⚠ PARTIAL: Received {len(received)} of {len(test_data)} bytes")
    print(f"    Got: {received}")
    print("    Possible timing or buffer issue")
else:
    print("✗ FAILURE: No data received")
    print("    Either:")
    print("    1. A-B not shorted properly")
    print("    2. UART TX not working")
    print("    3. UART RX not working")

print()
print("=" * 60)

ser.close()
