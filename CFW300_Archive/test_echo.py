#!/usr/bin/env python3
import serial
import time

print("Checking for TX echo vs VFD response...")
print("=" * 60)

# Send a distinctive pattern
test_packet = bytes([0xFF, 0xAA, 0x55, 0x12, 0x34, 0x56, 0x78, 0x90])

ser = serial.Serial("/dev/ttyUSB0", 19200, parity="E", stopbits=1, bytesize=8, timeout=1)
ser.rts = True
ser.dtr = True
time.sleep(0.1)

ser.reset_input_buffer()
print(f"TX: {test_packet.hex()}")
ser.write(test_packet)
time.sleep(0.5)

response = ser.read(100)
print(f"RX: {response.hex() if response else 'NONE'} ({len(response)} bytes)")

if response:
    if response == test_packet:
        print("  ** ECHO DETECTED ** - Receiving our own transmission!")
    elif response == test_packet[:len(response)]:
        print("  ** PARTIAL ECHO ** - Receiving part of our transmission!")
    else:
        print("  ** DIFFERENT DATA ** - This is from VFD or noise")

ser.close()
