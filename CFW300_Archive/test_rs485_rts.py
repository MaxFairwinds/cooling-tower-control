#!/usr/bin/env python3
"""
Test RS485 with RTS control for transmitter enable.
Many RS485 adapters use RTS to control the DE/RE pins.
"""

import serial
import time

PORT = '/dev/cu.usbserial-1420'
BAUD = 19200

print("RS485 Test with RTS Control")
print("=" * 50)
print(f"Port: {PORT}")
print(f"Baud rate: {BAUD}")
print()
print("Testing RTS=HIGH during transmission")
print("Measure voltage between A and B terminals")
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
    
    print(f"Opened {PORT}")
    print()
    
    # Test with RTS HIGH (enables RS485 transmitter on many adapters)
    print("Setting RTS=HIGH to enable RS485 transmitter...")
    ser.rts = True
    time.sleep(0.1)
    print(f"RTS state: {ser.rts}")
    print()
    print("Transmitting 0xAA continuously...")
    print("Check A-B voltage now!")
    print()
    
    packet_count = 0
    start_time = time.time()
    
    while True:
        # Send data with RTS HIGH
        ser.write(b'\xAA' * 10)
        packet_count += 1
        
        if packet_count % 50 == 0:
            elapsed = time.time() - start_time
            print(f"Sent {packet_count} packets | RTS={ser.rts} | {elapsed:.1f}s elapsed")
        
        time.sleep(0.02)

except KeyboardInterrupt:
    print("\n\nStopped by user")
    
except Exception as e:
    print(f"\nError: {e}")
    
finally:
    if 'ser' in locals() and ser.is_open:
        ser.rts = False  # Disable transmitter
        ser.close()
        print("Serial port closed, RTS=LOW")
