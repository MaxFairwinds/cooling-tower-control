#!/usr/bin/env python3
import serial
import time

# Open serial port with aggressive settings
ser = serial.Serial("/dev/ttyUSB0", 19200, parity="E", stopbits=1, bytesize=8, timeout=1)
ser.rts = True
ser.dtr = True
time.sleep(0.2)

print("Testing VFD parameters with 1.93V signal...")
print("=" * 60)

# Test different parameters
tests = {
    "P001": [0x01, 0x03, 0x00, 0x01, 0x00, 0x01, 0xD5, 0xCA],
    "P220": [0x01, 0x03, 0x00, 0xDC, 0x00, 0x01, 0x84, 0x36],
    "P308": [0x01, 0x03, 0x01, 0x34, 0x00, 0x01, 0xC4, 0x22],
    "P316": [0x01, 0x03, 0x01, 0x3C, 0x00, 0x01, 0x45, 0xFA],
}

for name, packet_list in tests.items():
    packet = bytes(packet_list)
    ser.reset_input_buffer()
    ser.write(packet)
    time.sleep(0.3)
    response = ser.read(100)
    
    tx_hex = " ".join(f"{b:02x}" for b in packet)
    rx_hex = " ".join(f"{b:02x}" for b in response) if response else "NONE"
    
    print(f"{name}:")
    print(f"  TX: {tx_hex}")
    print(f"  RX: {rx_hex} ({len(response)} bytes)")
    print()
    
    time.sleep(0.2)

ser.close()
print("Test complete")
