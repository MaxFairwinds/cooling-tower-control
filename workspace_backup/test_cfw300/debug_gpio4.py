#!/usr/bin/env python3
"""
Debug GPIO4 (RTS/Enable Pin)
Toggles GPIO4 every 5 seconds so you can measure if it affects the RS-485 output.
"""
import os
import time

print("=" * 60)
print("DEBUG GPIO4 (RTS/ENABLE PIN)")
print("=" * 60)
print()
print("This script will toggle GPIO4 (Pin 7) every 5 seconds.")
print("Please measure the voltage between A and B on the HAT.")
print()

# Setup GPIO4
gpio4_path = "/sys/class/gpio/gpio4"
try:
    if not os.path.exists(gpio4_path):
        with open("/sys/class/gpio/export", "w") as f:
            f.write("4")
        time.sleep(0.1)
except OSError:
    pass

# Set as output
try:
    with open(f"{gpio4_path}/direction", "w") as f:
        f.write("out")
except Exception as e:
    print(f"Error setting direction: {e}")

print("Starting toggle loop (Ctrl+C to stop)...")
print()

try:
    while True:
        # Set HIGH
        print("GPIO4 is HIGH (TX Mode?) -> Measure A-B voltage now")
        with open(f"{gpio4_path}/value", "w") as f:
            f.write("1")
        time.sleep(5)
        
        # Set LOW
        print("GPIO4 is LOW (RX Mode?)  -> Measure A-B voltage now")
        with open(f"{gpio4_path}/value", "w") as f:
            f.write("0")
        time.sleep(5)
        
except KeyboardInterrupt:
    print("\nStopped.")
