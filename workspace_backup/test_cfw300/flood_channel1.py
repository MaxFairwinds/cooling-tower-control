#!/usr/bin/env python3
"""
RS-485 Flood Test - Channel 1
Continuously sends data on Channel 1 (ttySC1) to allow voltmeter testing.
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
print("RS-485 FLOOD TEST (Channel 1)")
print("=" * 60)
print("Sending 'U' (0x55) continuously on /dev/ttySC1...")
print("Measure voltage between A and B on Channel 1.")
print("Press Ctrl+C to stop.")
print()

try:
    port1 = serial.Serial("/dev/ttySC1", baudrate=9600, timeout=1)
    
    # Set to Transmit Mode (LOW)
    set_pin_low(TXDEN_2)
    print("GPIO 22 set LOW (Transmit Mode)")
    
    while True:
        port1.write(b'U' * 50)
        port1.flush()
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nStopped.")
    set_pin_high(TXDEN_2)
    port1.close()
except Exception as e:
    print(f"\nERROR: {e}")
