#!/usr/bin/env python3
import serial
import time

print("Testing different RTS/DTR combinations...")
print("=" * 60)

# Read P001
packet = bytes([0x01, 0x03, 0x00, 0x01, 0x00, 0x01, 0xD5, 0xCA])

# Test 1: RTS/DTR False during TX and RX
print("\nTest 1: RTS=False, DTR=False")
ser = serial.Serial("/dev/ttyUSB0", 19200, parity="E", stopbits=1, bytesize=8, timeout=2)
ser.rts = False
ser.dtr = False
time.sleep(0.1)
ser.reset_input_buffer()
ser.write(packet)
time.sleep(0.5)
response = ser.read(100)
print(f"  RX: {response.hex() if response else 'NONE'} ({len(response)} bytes)")
ser.close()

# Test 2: RTS True, DTR False
print("\nTest 2: RTS=True, DTR=False")
ser = serial.Serial("/dev/ttyUSB0", 19200, parity="E", stopbits=1, bytesize=8, timeout=2)
ser.rts = True
ser.dtr = False
time.sleep(0.1)
ser.reset_input_buffer()
ser.write(packet)
ser.rts = False
time.sleep(0.5)
response = ser.read(100)
print(f"  RX: {response.hex() if response else 'NONE'} ({len(response)} bytes)")
ser.close()

# Test 3: DTR True, RTS False
print("\nTest 3: RTS=False, DTR=True")
ser = serial.Serial("/dev/ttyUSB0", 19200, parity="E", stopbits=1, bytesize=8, timeout=2)
ser.rts = False
ser.dtr = True
time.sleep(0.1)
ser.reset_input_buffer()
ser.write(packet)
ser.dtr = False
time.sleep(0.5)
response = ser.read(100)
print(f"  RX: {response.hex() if response else 'NONE'} ({len(response)} bytes)")
ser.close()

# Test 4: Both True (original)
print("\nTest 4: RTS=True, DTR=True (original)")
ser = serial.Serial("/dev/ttyUSB0", 19200, parity="E", stopbits=1, bytesize=8, timeout=2)
ser.rts = True
ser.dtr = True
time.sleep(0.1)
ser.reset_input_buffer()
ser.write(packet)
time.sleep(0.5)
response = ser.read(100)
print(f"  RX: {response.hex() if response else 'NONE'} ({len(response)} bytes)")
ser.close()

print("\nTest complete")
