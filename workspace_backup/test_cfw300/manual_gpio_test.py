#!/usr/bin/env python3
"""
Manual GPIO4 control loopback test.
Some RS-485 HATs need GPIO4 manually controlled instead of automatic ioctl.
"""
import serial
import time
import os

print("=" * 60)
print("MANUAL GPIO4 CONTROL LOOPBACK TEST")
print("=" * 60)
print()
print("Make sure A and B are shorted together!")
print()

# Setup GPIO4 for manual control
gpio4_path = "/sys/class/gpio/gpio4"
try:
    if not os.path.exists(gpio4_path):
        with open("/sys/class/gpio/export", "w") as f:
            f.write("4")
        time.sleep(0.1)
except OSError:
    # Already exported, that's fine
    pass

# Set GPIO4 as output
with open(f"{gpio4_path}/direction", "w") as f:
    f.write("out")

print("✓ GPIO4 configured as output")

# Open serial port
ser = serial.Serial('/dev/ttyAMA0', baudrate=9600, timeout=1)
print(f"✓ Serial port opened: {ser.port}")
print()

# Clear buffers
ser.reset_input_buffer()
ser.reset_output_buffer()

# Test with manual GPIO4 control
test_data = b"HELLO"
print(f"Sending: {test_data}")

# Set GPIO4 HIGH (enable transmit)
with open(f"{gpio4_path}/value", "w") as f:
    f.write("1")
print("  GPIO4 = HIGH (TX enabled)")

# Send data
ser.write(test_data)
ser.flush()

# Small delay for transmission to complete
time.sleep(0.05)

# Set GPIO4 LOW (enable receive)
with open(f"{gpio4_path}/value", "w") as f:
    f.write("0")
print("  GPIO4 = LOW (RX enabled)")

# Wait a bit for loopback
time.sleep(0.1)

# Read back
received = ser.read(len(test_data))
print(f"Received: {received}")
print()

if received == test_data:
    print("✓✓✓ SUCCESS! Manual GPIO4 control works!")
    print("    The HAT needs manual GPIO control, not automatic ioctl.")
    print("    This is the solution!")
elif len(received) > 0:
    print(f"⚠ PARTIAL: Got {len(received)} bytes: {received}")
else:
    print("✗ Still no data received")
    print("  Check:")
    print("  1. A-B wire connection")
    print("  2. GPIO4 polarity (try inverting HIGH/LOW)")

print()
print("=" * 60)

ser.close()
