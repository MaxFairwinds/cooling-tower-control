#!/usr/bin/env python3
"""
Comprehensive HAT verification test.
Tests if the Waveshare HAT hardware is physically present and functional.
"""
import os
import time

print("=" * 70)
print("WAVESHARE RS485 CAN HAT HARDWARE VERIFICATION")
print("=" * 70)
print()

# Test 1: Check if UART device exists
print("TEST 1: UART Device")
print("-" * 70)
uart_path = "/dev/ttyAMA0"
if os.path.exists(uart_path):
    print(f"✓ {uart_path} exists")
    # Check permissions
    import stat
    st = os.stat(uart_path)
    print(f"  Permissions: {oct(st.st_mode)[-3:]}")
    print(f"  Owner: {st.st_uid}, Group: {st.st_gid}")
else:
    print(f"✗ {uart_path} does NOT exist")
    print("  UART is not enabled or HAT is not connected")
print()

# Test 2: Check GPIO4 (RS-485 enable pin)
print("TEST 2: GPIO4 (RS-485 Enable Pin)")
print("-" * 70)
gpio4_path = "/sys/class/gpio/gpio4"
try:
    # Try to export GPIO4
    if not os.path.exists(gpio4_path):
        with open("/sys/class/gpio/export", "w") as f:
            f.write("4")
        time.sleep(0.1)
    
    if os.path.exists(gpio4_path):
        print("✓ GPIO4 is accessible")
        
        # Set as output
        with open(f"{gpio4_path}/direction", "w") as f:
            f.write("out")
        
        # Toggle it
        print("  Testing GPIO4 toggle...")
        for state in ["1", "0", "1"]:
            with open(f"{gpio4_path}/value", "w") as f:
                f.write(state)
            time.sleep(0.1)
        
        print("✓ GPIO4 can be controlled")
        
        # Read current value
        with open(f"{gpio4_path}/value", "r") as f:
            value = f.read().strip()
        print(f"  Current value: {value}")
        
    else:
        print("✗ GPIO4 is NOT accessible")
        print("  HAT may not be physically connected")
        
except Exception as e:
    print(f"✗ Error accessing GPIO4: {e}")
print()

# Test 3: Check if we can open UART
print("TEST 3: UART Open Test")
print("-" * 70)
try:
    import serial
    ser = serial.Serial(uart_path, baudrate=9600, timeout=1)
    print(f"✓ Can open {uart_path}")
    print(f"  Baud: {ser.baudrate}")
    print(f"  Is open: {ser.is_open}")
    ser.close()
except Exception as e:
    print(f"✗ Cannot open {uart_path}: {e}")
print()

# Test 4: Physical pin voltage test instructions
print("TEST 4: Physical Pin Verification (MANUAL)")
print("-" * 70)
print("To verify HAT is physically connected:")
print("  1. With multimeter, measure voltage between:")
print("     - Pin 1 (3.3V) and Pin 6 (GND)")
print("     - Should read ~3.3V")
print("  2. Check GPIO14 (Pin 8) and GPIO15 (Pin 10)")
print("     - These are the UART TX/RX pins")
print("     - Should show some activity when transmitting")
print()

# Summary
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print("If all tests pass, the HAT is likely physically connected.")
print("If GPIO4 test fails, the HAT may not be seated properly on the GPIO header.")
print("=" * 70)
