#!/usr/bin/env python3
import serial
import time

print("Quick Modbus test with single termination (2.55V)")
print("=" * 60)

ser = serial.Serial("/dev/ttyUSB0", 19200, parity="E", timeout=0.5)
time.sleep(0.2)

# Read P001
packet = bytes([0x01, 0x03, 0x00, 0x01, 0x00, 0x01, 0xD5, 0xCA])

for i in range(3):
    print(f"\nAttempt {i+1}:")
    ser.reset_input_buffer()
    
    print(f"  TX: {packet.hex()}")
    ser.write(packet)
    
    time.sleep(0.3)
    response = ser.read(100)
    
    print(f"  RX: {response.hex() if response else 'NONE'} ({len(response)} bytes)")
    
    if response and len(response) >= 7:
        print("  ** SUCCESS! **")
        if response[0] == 0x01 and response[1] == 0x03:
            byte_count = response[2]
            data = response[3:3+byte_count]
            if len(data) == 2:
                value = int.from_bytes(data, byteorder='big')
                print(f"  P001 value: {value}")
        break
    elif response:
        print(f"  Partial/corrupt response")

ser.close()
print("\nTest complete")
