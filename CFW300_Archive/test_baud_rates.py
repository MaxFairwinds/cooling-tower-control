#!/usr/bin/env python3
import serial
import time

print("Testing different baud rates...")
print("=" * 60)

# Read P001
packet = bytes([0x01, 0x03, 0x00, 0x01, 0x00, 0x01, 0xD5, 0xCA])

baud_rates = [9600, 19200, 38400, 57600, 115200]

for baud in baud_rates:
    print(f"\nTesting {baud} baud:")
    ser = serial.Serial("/dev/ttyUSB0", baud, parity="E", stopbits=1, bytesize=8, timeout=1)
    ser.rts = True
    ser.dtr = True
    time.sleep(0.1)
    
    ser.reset_input_buffer()
    ser.write(packet)
    time.sleep(0.3)
    
    response = ser.read(100)
    print(f"  RX: {response.hex() if response else 'NONE'} ({len(response)} bytes)")
    
    if response and len(response) > 1:
        print(f"  SUCCESS! Bytes: {' '.join(f'{b:02x}' for b in response)}")
    
    ser.close()
    time.sleep(0.2)

print("\nTest complete")
