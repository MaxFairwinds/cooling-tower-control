#!/usr/bin/env python3
"""
RS-485 Loopback Test with GPIO Direction Control
Uses GPIO 27 (TXDEN_1) and GPIO 22 (TXDEN_2) for transceiver direction.
"""
import serial
import time
import subprocess

# GPIO pins for TX Enable
TXDEN_1 = 27  # Channel 0 direction
TXDEN_2 = 22  # Channel 1 direction

def setup_gpio(pin):
    """Export and set GPIO as output HIGH using sysfs"""
    try:
        # Export if not already
        with open('/sys/class/gpio/export', 'w') as f:
            f.write(str(pin))
    except:
        pass  # Already exported
    
    # Set direction to output
    with open(f'/sys/class/gpio/gpio{pin}/direction', 'w') as f:
        f.write('out')
    
    # Set HIGH (receive mode by default)
    with open(f'/sys/class/gpio/gpio{pin}/value', 'w') as f:
        f.write('1')

def set_gpio(pin, value):
    """Set GPIO value (0 or 1)"""
    with open(f'/sys/class/gpio/gpio{pin}/value', 'w') as f:
        f.write(str(value))

print("=" * 60)
print("RS-485 LOOPBACK TEST (With GPIO Direction Control)")
print("=" * 60)
print()

try:
    # Setup direction control GPIOs
    print("Setting up GPIO 27 and 22 for direction control...")
    setup_gpio(TXDEN_1)
    setup_gpio(TXDEN_2)
    print("GPIOs configured (HIGH = receive mode)")
    print()

    # Open both ports at 115200 (Waveshare default)
    port0 = serial.Serial("/dev/ttySC0", baudrate=115200, timeout=2)
    port1 = serial.Serial("/dev/ttySC1", baudrate=115200, timeout=2)
    
    print(f"Opened {port0.port} and {port1.port}")
    print()

    # Clear buffers
    port0.reset_input_buffer()
    port1.reset_input_buffer()

    # Test 1: Port 0 -> Port 1
    msg1 = b"HELLO_FROM_0\r\n"
    print(f"Sending from {port0.port}: {msg1}")
    port0.write(msg1)
    port0.flush()
    time.sleep(0.2)
    
    recv1 = port1.read(len(msg1))
    print(f"Received on {port1.port}:  {recv1}")
    
    if msg1 == recv1:
        print("✓ PASS: Port 0 -> Port 1")
    elif recv1 == b'':
        print("✗ FAIL: No data received (timeout)")
    else:
        print(f"✗ FAIL: Data mismatch")
    print()

    # Test 2: Port 1 -> Port 0
    msg2 = b"HELLO_FROM_1\r\n"
    print(f"Sending from {port1.port}: {msg2}")
    port1.write(msg2)
    port1.flush()
    time.sleep(0.2)
    
    recv2 = port0.read(len(msg2))
    print(f"Received on {port0.port}:  {recv2}")
    
    if msg2 == recv2:
        print("✓ PASS: Port 1 -> Port 0")
    elif recv2 == b'':
        print("✗ FAIL: No data received (timeout)")
    else:
        print(f"✗ FAIL: Data mismatch")

    port0.close()
    port1.close()

except Exception as e:
    import traceback
    print(f"\nERROR: {e}")
    traceback.print_exc()

print()
print("=" * 60)
