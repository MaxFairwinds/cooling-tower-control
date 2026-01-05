#!/usr/bin/env python3
import serial
import time
import struct

PORT = "/dev/ttyUSB0"
BAUD = 19200
VFD_ADDRESS = 1

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
    return struct.pack("<H", crc)

def read_holding_register(address, register, count=1):
    """Read holding registers (function code 0x03)"""
    request = bytes([address, 0x03, register >> 8, register & 0xFF, count >> 8, count & 0xFF])
    request += calculate_crc(request)
    return request

print("Modbus VFD Communication Test")
print("=" * 60)
print(f"Port: {PORT}")
print(f"VFD Address: {VFD_ADDRESS}")
print(f"Baud: {BAUD}, 8E1")
print()
print("VFD Parameters:")
print("  P308=1 (Address 1)")
print("  P310=1 (19200 baud)")  
print("  P311=1 (8E1)")
print("  P312=2 (Modbus RTU)")
print("=" * 60)
print()

try:
    ser = serial.Serial(
        port=PORT,
        baudrate=BAUD,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_EVEN,
        stopbits=serial.STOPBITS_ONE,
        timeout=1
    )
    
    # Aggressive control for 2.59V output
    ser.rts = True
    ser.dtr = True
    
    print(f"Port opened (RTS={ser.rts}, DTR={ser.dtr})")
    print()
    
    # Test 1: Read P002 (software version)
    print("Test 1: Reading P002 (software version)...")
    request = read_holding_register(VFD_ADDRESS, 0x0002, 1)
    print(f"TX: {request.hex(' ')}")
    
    ser.reset_input_buffer()
    ser.write(request)
    ser.flush()
    time.sleep(0.1)
    
    response = ser.read(100)
    print(f"RX: {response.hex(' ') if response else '(no response)'}")
    print(f"RX bytes: {len(response)}")
    print()
    
    # Test 2: Read P316 (RS485 status)
    print("Test 2: Reading P316 (RS485 communication status)...")
    request = read_holding_register(VFD_ADDRESS, 0x0316, 1)
    print(f"TX: {request.hex(' ')}")
    
    ser.reset_input_buffer()
    ser.write(request)
    ser.flush()
    time.sleep(0.1)
    
    response = ser.read(100)
    print(f"RX: {response.hex(' ') if response else '(no response)'}")
    print(f"RX bytes: {len(response)}")
    
    if len(response) >= 5:
        value = (response[3] << 8) | response[4]
        print(f"P316 value: {value}")
        print("  0 = No communication")
        print("  1 = Communication OK")
    print()
    
    # Test 3: Read P001 (motor RPM)
    print("Test 3: Reading P001 (motor RPM)...")
    request = read_holding_register(VFD_ADDRESS, 0x0001, 1)
    print(f"TX: {request.hex(' ')}")
    
    ser.reset_input_buffer()
    ser.write(request)
    ser.flush()
    time.sleep(0.1)
    
    response = ser.read(100)
    print(f"RX: {response.hex(' ') if response else '(no response)'}")
    print(f"RX bytes: {len(response)}")
    
    if len(response) >= 5:
        value = (response[3] << 8) | response[4]
        print(f"P001 value: {value} RPM")
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    if "ser" in locals() and ser.is_open:
        ser.close()
    print("\nTest complete")
