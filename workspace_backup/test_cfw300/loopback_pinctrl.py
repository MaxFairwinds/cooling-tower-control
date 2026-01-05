#!/usr/bin/env python3
"""
RS-485 Loopback Test with pinctrl Direction Control
Uses 'pinctrl' command to manage GPIO 27 (TXDEN_1) and GPIO 22 (TXDEN_2).
Bypasses RPi.GPIO/lgpio library issues.
"""
import serial
import time
import subprocess

# GPIO pins for TX Enable
TXDEN_1 = 27  # Channel 0 direction
TXDEN_2 = 22  # Channel 1 direction

def set_pin_high(pin):
    """Set pin to Output High (Transmit Mode)"""
    try:
        subprocess.run(["pinctrl", "set", str(pin), "op", "dh"], check=True, stdout=subprocess.DEVNULL)
    except Exception as e:
        print(f"Error setting pin {pin} HIGH: {e}")

def set_pin_low(pin):
    """Set pin to Output Low (Receive Mode)"""
    try:
        subprocess.run(["pinctrl", "set", str(pin), "op", "dl"], check=True, stdout=subprocess.DEVNULL)
    except Exception as e:
        print(f"Error setting pin {pin} LOW: {e}")

print("=" * 60)
print("RS-485 LOOPBACK TEST (With pinctrl Direction Control)")
print("=" * 60)
print()

try:
    # Open both ports
    port0 = serial.Serial("/dev/ttySC0", baudrate=115200, timeout=1)
    port1 = serial.Serial("/dev/ttySC1", baudrate=115200, timeout=1)
    
    print(f"Opened {port0.port} and {port1.port}")
    print()

    # Clear buffers
    port0.reset_input_buffer()
    port1.reset_input_buffer()

    # Test 1: Port 0 (TX) -> Port 1 (RX)
    print("Test 1: Port 0 -> Port 1")
    
    # Logic from C code: 0=TX, 1=RX
    set_pin_high(TXDEN_2) # Port 1 RX (High)
    set_pin_low(TXDEN_1)  # Port 0 TX (Low)
    time.sleep(0.01)      # Stabilization time

    msg1 = b"HELLO_FROM_0\r\n"
    print(f"  Sending: {msg1}")
    port0.write(msg1)
    port0.flush()         # Wait for data to leave UART
    time.sleep(0.05)      # Extra hold time for transceiver
    
    set_pin_high(TXDEN_1) # Port 0 back to RX
    
    time.sleep(0.1)
    
    recv1 = port1.read(len(msg1))
    print(f"  Received: {recv1}")
    
    if msg1 == recv1:
        print("  ✓ PASS")
    else:
        print("  ✗ FAIL")
    print()

    # Test 2: Port 1 (TX) -> Port 0 (RX)
    print("Test 2: Port 1 -> Port 0")
    
    # Logic from C code: 0=TX, 1=RX
    set_pin_high(TXDEN_1) # Port 0 RX (High)
    set_pin_low(TXDEN_2)  # Port 1 TX (Low)
    time.sleep(0.01)

    msg2 = b"HELLO_FROM_1\r\n"
    print(f"  Sending: {msg2}")
    port1.write(msg2)
    port1.flush()
    time.sleep(0.05)
    
    set_pin_high(TXDEN_2) # Port 1 back to RX
    
    time.sleep(0.1)
    
    recv2 = port0.read(len(msg2))
    print(f"  Received: {recv2}")
    
    if msg2 == recv2:
        print("  ✓ PASS")
    else:
        print("  ✗ FAIL")

    port0.close()
    port1.close()

except Exception as e:
    print(f"\nERROR: {e}")

print()
print("=" * 60)
