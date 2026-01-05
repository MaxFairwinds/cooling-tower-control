#!/usr/bin/env python3
"""
Test RS485 with steady HIGH (0xFF) to produce stable DC voltage.
This sends continuous 1's which should create a steady differential voltage.
"""

import serial
import time

PORT = '/dev/cu.usbserial-1420'
BAUD = 19200

print("RS485 Steady DC Voltage Test")
print("=" * 50)
print("Sending continuous 0xFF (all bits HIGH)")
print("This should produce STEADY DC voltage on A-B")
print()
print("Make sure your multimeter is set to DC VOLTAGE")
print()
print("Press Ctrl+C to stop")
print("=" * 50)
print()

try:
    ser = serial.Serial(
        port=PORT,
        baudrate=BAUD,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_EVEN,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.1
    )
    
    # Enable RS485 transmitter with RTS
    ser.rts = True
    ser.dtr = False
    
    print(f"Opened {PORT}")
    print(f"RTS=HIGH (RS485 enabled)")
    print()
    print("Transmitting continuous 0xFF bytes...")
    print("Measure STEADY DC voltage on A-B now!")
    print()
    
    byte_count = 0
    start = time.time()
    
    while True:
        # Send 0xFF (all 1's) - creates steady high signal
        ser.write(b'\xFF' * 20)
        byte_count += 20
        
        if byte_count % 1000 == 0:
            elapsed = time.time() - start
            print(f"Sent {byte_count} bytes (0xFF) | {elapsed:.1f}s | What DC voltage do you see?")
        
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n\nStopped by user")
    
except Exception as e:
    print(f"\nError: {e}")
    
finally:
    if 'ser' in locals() and ser.is_open:
        ser.rts = False
        ser.close()
        print("Serial port closed")
