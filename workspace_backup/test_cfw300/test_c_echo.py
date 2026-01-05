#!/usr/bin/env python3
"""
Test C Echo Server
Interacts with the official Waveshare 'main' C program running on Channel 0.
This script runs on Channel 1.
"""
import serial
import time
import subprocess

# GPIO pins for TX Enable
TXDEN_2 = 22  # Channel 1 direction

def set_pin_low(pin):
    subprocess.run(["pinctrl", "set", str(pin), "op", "dl"], check=True, stdout=subprocess.DEVNULL)

def set_pin_high(pin):
    subprocess.run(["pinctrl", "set", str(pin), "op", "dh"], check=True, stdout=subprocess.DEVNULL)

print("=" * 60)
print("TESTING C ECHO SERVER")
print("=" * 60)

try:
    # Open Port 1
    port1 = serial.Serial("/dev/ttySC1", baudrate=9600, timeout=2)
    print(f"Opened {port1.port}")
    
    # Set to Receive Mode (HIGH)
    set_pin_high(TXDEN_2)
    print("GPIO 22 set HIGH (Receive Mode)")
    
    # 1. Listen for startup message
    print("Listening for startup message from C program...")
    startup = port1.read_until(b'\n')
    print(f"Received: {startup}")
    
    if b"Waveshare" in startup:
        print("✓ Startup message received!")
    else:
        print("? No startup message (maybe missed it)")

    # 2. Send Data
    msg = b"TEST_ECHO\n"
    print(f"Sending: {msg}")
    
    set_pin_low(TXDEN_2) # TX
    time.sleep(0.01)
    port1.write(msg)
    port1.flush()
    time.sleep(0.05)
    set_pin_high(TXDEN_2) # RX
    
    # 3. Read Echo
    print("Waiting for echo...")
    echo = port1.read_until(b'\n')
    print(f"Received: {echo}")
    
    if msg.strip() in echo:
        print("✓ PASS: Echo received")
    else:
        print("✗ FAIL: No echo")

    port1.close()

except Exception as e:
    print(f"\nERROR: {e}")
