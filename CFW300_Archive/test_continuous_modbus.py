#!/usr/bin/env python3
import serial
import time

print("Continuous Modbus transmission test")
print("Measure voltage at adapter terminals NOW")
print("Press Ctrl+C to stop")
print("=" * 60)

ser = serial.Serial("/dev/ttyUSB0", 19200, parity="E", stopbits=1, bytesize=8, timeout=0.5)
ser.rts = True
ser.dtr = True
time.sleep(0.1)

# Read P001 packet
packet = bytes([0x01, 0x03, 0x00, 0x01, 0x00, 0x01, 0xD5, 0xCA])

count = 0
try:
    while True:
        ser.reset_input_buffer()
        ser.write(packet)
        time.sleep(0.05)  # 50ms between transmissions
        response = ser.read(100)
        
        count += 1
        if count % 20 == 0:  # Print every 20 packets
            print(f"Sent {count} packets - Last RX: {response.hex() if response else 'NONE'} ({len(response)} bytes)")
        
except KeyboardInterrupt:
    print(f"\nStopped after {count} packets")
    ser.close()
