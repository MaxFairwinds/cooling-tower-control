#!/usr/bin/env python3
import serial
import time

PORT = "/dev/ttyUSB0"
BAUD = 19200
VFD_ADDRESS = 1

def calculate_crc(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

print("Continuous Modbus Transmission Test")
print("=" * 60)
print(f"Device: {PORT}")
print("Sending Modbus read requests continuously")
print("Measure A-B voltage on screw terminals NOW")
print("Press Ctrl+C to stop")
print("=" * 60)
print()

ser = serial.Serial(
    port=PORT,
    baudrate=BAUD,
    bytesize=8,
    parity='E',
    stopbits=1,
    timeout=0.5
)

ser.rts = True
ser.dtr = True

count = 0
try:
    while True:
        # Read P001 (same packet as before)
        packet = bytes([VFD_ADDRESS, 0x03, 0x00, 0x01, 0x00, 0x01])
        crc = calculate_crc(packet)
        packet += bytes([crc & 0xFF, (crc >> 8) & 0xFF])
        
        ser.write(packet)
        time.sleep(0.010)  # 10ms between packets - higher duty cycle
        
        # Clear any response
        ser.reset_input_buffer()
        
        count += 1
        if count % 20 == 0:
            print(f"Sent {count} packets...")
            
except KeyboardInterrupt:
    print(f"\nStopped. Sent {count} packets total.")
    ser.close()
