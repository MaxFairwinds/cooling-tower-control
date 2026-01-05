#!/usr/bin/env python3
"""
RS-485 Flood Test with pinctrl Direction Control
Continuously sends data on Channel 0 (ttySC0) to allow voltmeter testing.
"""
import serial
import time
import subprocess

# GPIO pins for TX Enable
TXDEN_1 = 27  # Channel 0 direction

def set_pin_low(pin):
    """Set pin to Output Low (Transmit Mode)"""
    try:
        subprocess.run(["pinctrl", "set", str(pin), "op", "dl"], check=True, stdout=subprocess.DEVNULL)
    except Exception as e:
        print(f"Error setting pin {pin} LOW: {e}")

def set_pin_high(pin):
    """Set pin to Output High (Receive Mode)"""
    try:
        subprocess.run(["pinctrl", "set", str(pin), "op", "dh"], check=True, stdout=subprocess.DEVNULL)
    except Exception as e:
        print(f"Error setting pin {pin} HIGH: {e}")

print("=" * 60)
print("RS-485 FLOOD TEST (Channel 0)")
print("=" * 60)
print("Sending 'U' (0x55) continuously on /dev/ttySC0...")
print("Measure voltage between A and B on Channel 0.")
print("Press Ctrl+C to stop.")
print()

try:
    port0 = serial.Serial("/dev/ttySC0", baudrate=9600, timeout=1)
    
    # Set to Transmit Mode (LOW)
    set_pin_low(TXDEN_1)
    print("GPIO 27 set LOW (Transmit Mode)")
    
    while True:
        port0.write(b'U' * 50)
        port0.flush()
        # Keep sending...
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nStopped.")
    set_pin_high(TXDEN_1) # Reset to RX
    port0.close()
except Exception as e:
    print(f"\nERROR: {e}")
