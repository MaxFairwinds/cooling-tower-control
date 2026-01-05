#!/usr/bin/env python3
"""
Test Modbus control - try to start motor via Modbus
"""
import serial
import time

PORT = '/dev/ttyUSB0'
BAUD = 19200

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

ser = serial.Serial(
    port=PORT,
    baudrate=BAUD,
    bytesize=8,
    parity='E',
    stopbits=1,
    timeout=1.0
)

print("="*60)
print("MODBUS MOTOR CONTROL TEST")
print("="*60)
print()

# Step 1: Write speed reference to P683 (10 Hz = ~1365 in 13-bit scale for 60Hz motor)
# Speed scale: 8192 = rated freq (60Hz), so 10Hz = 8192 * 10/60 = 1365
print("Step 1: Writing speed reference to P683 (10 Hz)")
print("-"*60)

slave_addr = 1
function = 0x06  # Write Single Register
register = 683   # P683 - Speed Reference
value = 1365     # ~10 Hz (adjust if P403 != 60Hz)

request = bytearray([
    slave_addr,
    function,
    (register >> 8) & 0xFF,
    register & 0xFF,
    (value >> 8) & 0xFF,
    value & 0xFF
])

crc = calculate_crc(request)
request.append(crc & 0xFF)
request.append((crc >> 8) & 0xFF)

print(f"TX: {' '.join(f'{b:02X}' for b in request)}")
ser.reset_input_buffer()
ser.write(request)
ser.flush()
time.sleep(0.1)

response = ser.read(100)
print(f"RX: {' '.join(f'{b:02X}' for b in response) if response else 'NONE'}")
print()

# Step 2: Write control word to P682 - Enable and Run
print("Step 2: Writing control word to P682 (Enable + Run Forward)")
print("-"*60)

register = 682   # P682 - Control Word
# Bit 0: Run/Stop = 1
# Bit 1: General Enable = 1  
# Bit 2: Direction Forward = 1
# Bit 4: Remote mode = 1
value = 0b00010111  # Bits: 4,2,1,0 = 0x17

request = bytearray([
    slave_addr,
    function,
    (register >> 8) & 0xFF,
    register & 0xFF,
    (value >> 8) & 0xFF,
    value & 0xFF
])

crc = calculate_crc(request)
request.append(crc & 0xFF)
request.append((crc >> 8) & 0xFF)

print(f"TX: {' '.join(f'{b:02X}' for b in request)}")
ser.reset_input_buffer()
ser.write(request)
ser.flush()
time.sleep(0.1)

response = ser.read(100)
print(f"RX: {' '.join(f'{b:02X}' for b in response) if response else 'NONE'}")
print()

print("Check VFD display - is motor running?")
print("Check P316 - did it increment?")
print()

ser.close()
