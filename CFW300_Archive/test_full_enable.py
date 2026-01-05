#!/usr/bin/env python3
"""
Test if we can get full 5V RS485 differential.
According to SP485E datasheet:
- DE (Driver Enable) must be HIGH to transmit
- RE (Receiver Enable) is active-LOW, so must be HIGH during transmit
- With 27Ω load, should get minimum 1.5V differential
- With no load, should get even more

The 0.14V we're seeing suggests DE/RE aren't fully enabled.
"""

import serial
import time

PORT = '/dev/cu.usbserial-1420'
BAUD = 19200

print("SP485E Full Enable Test")
print("=" * 60)
print("According to SP485E datasheet:")
print("  - DE (pin 3) must be HIGH for transmit")
print("  - RE (pin 2) must be HIGH (disabled) for transmit")
print("  - Should produce 1.5-5V differential")
print()
print("Current result: 0.14V differential with RTS=HIGH")
print()
print("Testing with RTS=HIGH and DTR=HIGH simultaneously")
print("=" * 60)
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
    
    # Try both RTS and DTR HIGH - maybe both control DE and RE
    print("Setting RTS=HIGH and DTR=HIGH...")
    ser.rts = True
    ser.dtr = True
    time.sleep(0.2)
    
    print(f"RTS: {ser.rts}")
    print(f"DTR: {ser.dtr}")
    print()
    print("Transmitting 0x00 (all LOW bits) for 5 seconds...")
    print("Measure A-B voltage - should be NEGATIVE if working")
    print()
    
    for i in range(5):
        ser.write(b'\x00' * 20)
        print(f"{i+1}s - Sending 0x00 (LOW)")
        time.sleep(1)
    
    print()
    print("Now transmitting 0xFF (all HIGH bits) for 5 seconds...")  
    print("Measure A-B voltage - should be POSITIVE if working")
    print()
    
    for i in range(5):
        ser.write(b'\xFF' * 20)
        print(f"{i+1}s - Sending 0xFF (HIGH)")
        time.sleep(1)
    
    print()
    print("What voltages did you see?")
    print("0x00: A-B = ? V")
    print("0xFF: A-B = ? V")
    
except KeyboardInterrupt:
    print("\nStopped")
    
except Exception as e:
    print(f"Error: {e}")
    
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("\nPort closed")
