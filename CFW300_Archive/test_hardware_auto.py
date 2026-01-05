#!/usr/bin/env python3
import serial
import time

print("Proper Modbus test - relying on hardware automatic control")
print("Not touching RTS/DTR - let the hardware handle it")
print("=" * 60)

# Open port without forcing RTS/DTR
ser = serial.Serial("/dev/ttyUSB0", 19200, parity="E", stopbits=1, bytesize=8, timeout=2)

print("Port opened - hardware auto control active")
print("Waiting for line to stabilize...")
time.sleep(0.5)

# Read P001
packet = bytes([0x01, 0x03, 0x00, 0x01, 0x00, 0x01, 0xD5, 0xCA])

for attempt in range(5):
    print(f"\nAttempt {attempt + 1}:")
    ser.reset_input_buffer()
    
    # Just write - hardware handles TX enable
    ser.write(packet)
    print(f"  TX: {packet.hex()}")
    
    # Hardware automatically switches to RX
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
    
    time.sleep(0.5)

ser.close()
print("\nTest complete - measure voltage during this test")
