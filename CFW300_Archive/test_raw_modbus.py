#!/usr/bin/env python3
"""
Raw Modbus test - show exactly what we send and receive
"""
import serial
import time

PORT = '/dev/ttyUSB0'
BAUD = 19200

def calculate_crc(data):
    """Calculate Modbus RTU CRC16"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

# Open port
ser = serial.Serial(
    port=PORT,
    baudrate=BAUD,
    bytesize=8,
    parity='E',
    stopbits=1,
    timeout=1.0
)

print("="*60)
print("RAW MODBUS TEST")
print("="*60)
print(f"Port: {PORT}")
print(f"Baud: {BAUD}, 8E1")
print()

# Test reading P680 (Status Word) - register 680
# This is documented as "always readable" monitoring register
print("Test 1: Read P680 (Status Word) - Register 680 (0x2A8)")
print("-"*60)

slave_addr = 1
function = 0x03  # Read Holding Registers
register = 680   # P680
count = 1

# Build request
request = bytearray([
    slave_addr,
    function,
    (register >> 8) & 0xFF,
    register & 0xFF,
    (count >> 8) & 0xFF,
    count & 0xFF
])

crc = calculate_crc(request)
request.append(crc & 0xFF)
request.append((crc >> 8) & 0xFF)

print(f"TX ({len(request)} bytes): {' '.join(f'{b:02X}' for b in request)}")

# Clear buffers
ser.reset_input_buffer()
ser.reset_output_buffer()

# Send
ser.write(request)
ser.flush()
time.sleep(0.1)

# Receive
response = ser.read(100)
print(f"RX ({len(response)} bytes): {' '.join(f'{b:02X}' for b in response) if response else 'NONE'}")

if len(response) > 0:
    print(f"Raw bytes: {response}")
    
print()

# Test 2: Try P681 (Motor Speed)
print("Test 2: Read P681 (Motor Speed) - Register 681 (0x2A9)")
print("-"*60)

register = 681   # P681

request = bytearray([
    slave_addr,
    function,
    (register >> 8) & 0xFF,
    register & 0xFF,
    (count >> 8) & 0xFF,
    count & 0xFF
])

crc = calculate_crc(request)
request.append(crc & 0xFF)
request.append((crc >> 8) & 0xFF)

print(f"TX ({len(request)} bytes): {' '.join(f'{b:02X}' for b in request)}")

ser.reset_input_buffer()
ser.write(request)
ser.flush()
time.sleep(0.1)

response = ser.read(100)
print(f"RX ({len(response)} bytes): {' '.join(f'{b:02X}' for b in response) if response else 'NONE'}")

if len(response) > 0:
    print(f"Raw bytes: {response}")

print()

# Test 3: Disconnect VFD and see what we get (to identify echo)
print("Test 3: Read with long timeout (checking for echo)")
print("-"*60)

register = 316   # P316

request = bytearray([
    slave_addr,
    function,
    (register >> 8) & 0xFF,
    register & 0xFF,
    (count >> 8) & 0xFF,
    count & 0xFF
])

crc = calculate_crc(request)
request.append(crc & 0xFF)
request.append((crc >> 8) & 0xFF)

print(f"TX ({len(request)} bytes): {' '.join(f'{b:02X}' for b in request)}")

ser.reset_input_buffer()
tx_time = time.time()
ser.write(request)
ser.flush()

# Wait and show bytes as they arrive
response = bytearray()
while time.time() - tx_time < 0.5:
    if ser.in_waiting > 0:
        byte = ser.read(1)
        response.extend(byte)
        print(f"  Byte {len(response)} arrived at +{(time.time()-tx_time)*1000:.1f}ms: {byte[0]:02X}")
    time.sleep(0.01)

print(f"Total RX: {len(response)} bytes")

ser.close()
print("\nDone.")
