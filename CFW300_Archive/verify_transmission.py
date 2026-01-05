#!/usr/bin/env python3
"""
Transmission Verification Script
Sends Modbus request and shows exact bytes being transmitted
"""

import serial
import time

def calculate_modbus_crc(data):
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

def create_modbus_request(slave_id, function_code, start_addr, count):
    """Create a Modbus RTU request packet"""
    data = bytearray([
        slave_id,
        function_code,
        (start_addr >> 8) & 0xFF,
        start_addr & 0xFF,
        (count >> 8) & 0xFF,
        count & 0xFF
    ])
    crc = calculate_modbus_crc(data)
    data.append(crc & 0xFF)
    data.append((crc >> 8) & 0xFF)
    return bytes(data)

print("=" * 60)
print("CFW300 TRANSMISSION VERIFICATION")
print("=" * 60)

# Open serial port
port = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=19200,
    bytesize=8,
    parity='E',
    stopbits=1,
    timeout=1
)

print(f"\nPort: {port.name}")
print(f"Baud: {port.baudrate}")
print(f"Config: 8E1")
print(f"Port open: {port.is_open}")

# Create request to read P001 (register address 1)
slave_id = 1
function = 0x03  # Read Holding Registers
register = 1     # P001
count = 1

request = create_modbus_request(slave_id, function, register, count)

print(f"\n--- MODBUS REQUEST ---")
print(f"Slave ID: {slave_id}")
print(f"Function: 0x{function:02X} (Read Holding Registers)")
print(f"Register: {register} (P001)")
print(f"Count: {count}")
print(f"\nBytes to send: {' '.join(f'{b:02X}' for b in request)}")
print(f"Packet length: {len(request)} bytes")

# Verify CRC manually
expected_crc = calculate_modbus_crc(request[:-2])
packet_crc = request[-2] | (request[-1] << 8)
print(f"\nCRC Check:")
print(f"  Calculated: 0x{expected_crc:04X}")
print(f"  In packet:  0x{packet_crc:04X}")
print(f"  Valid: {'✓' if expected_crc == packet_crc else '✗'}")

# Send request
print(f"\n--- TRANSMITTING ---")
port.write(request)
port.flush()
print("✓ Request sent")
print("✓ Buffer flushed")

# Wait for response
print(f"\n--- WAITING FOR RESPONSE (timeout={port.timeout}s) ---")
time.sleep(0.1)
bytes_available = port.in_waiting
print(f"Bytes in buffer: {bytes_available}")

if bytes_available > 0:
    response = port.read(bytes_available)
    print(f"\n✓ RECEIVED {len(response)} bytes:")
    print(f"  Hex: {' '.join(f'{b:02X}' for b in response)}")
    print(f"  Dec: {' '.join(f'{b:3d}' for b in response)}")
    
    # Try to parse response
    if len(response) >= 5:
        resp_slave = response[0]
        resp_func = response[1]
        resp_bytes = response[2]
        
        print(f"\n--- RESPONSE PARSING ---")
        print(f"Slave ID: {resp_slave}")
        print(f"Function: 0x{resp_func:02X}")
        print(f"Byte count: {resp_bytes}")
        
        if resp_func & 0x80:
            print(f"✗ EXCEPTION RESPONSE!")
            print(f"  Exception code: {resp_bytes}")
        elif len(response) >= 5 + resp_bytes:
            value = (response[3] << 8) | response[4]
            print(f"✓ Register value: {value}")
else:
    print("✗ NO RESPONSE (0 bytes)")
    print("\nThis confirms VFD is not responding.")
    print("Check:")
    print("  1. P316 on VFD (should be 1 if receiving)")
    print("  2. Wiring A/B connections")
    print("  3. VFD RS485 module installed and functional")

port.close()
print("\n" + "=" * 60)
