#!/usr/bin/env python3
"""
Modbus communication with high-drive mode (multiple port opens for 2.7V output).
This maintains the voltage boost while communicating with the VFD.
"""

import serial
import time
import struct

PORT = '/dev/cu.usbserial-1420'
BAUD = 19200
VFD_ADDRESS = 1

def calculate_crc(data):
    """Calculate Modbus RTU CRC16."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return struct.pack('<H', crc)

print("High-Drive Modbus RTU Communication")
print("=" * 60)
print("Using voltage boost technique (2.7V output)")
print()
print("Connect VFD now: A-to-A, B-to-B")
print("=" * 60)
print()

# Open multiple connections to maintain high voltage
boosters = []
try:
    print("Opening boost connections...")
    for i in range(3):  # Open 3 additional connections for voltage boost
        try:
            boost = serial.Serial(PORT, BAUD, timeout=0.01)
            boost.rts = True
            boost.dtr = True
            boosters.append(boost)
            print(f"  Boost {i+1} opened")
        except:
            pass
    
    time.sleep(0.2)
    
    # Main communication port
    ser = serial.Serial(
        port=PORT,
        baudrate=BAUD,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_EVEN,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.5
    )
    
    ser.rts = True
    ser.dtr = True
    
    print(f"\nMain port opened: {PORT}")
    print(f"Total connections: {len(boosters) + 1}")
    print()
    print("Voltage should be ~2.7V - confirm with multimeter")
    input("Press Enter when ready to communicate with VFD...")
    print()
    
    # Read holding register 1 (P001 - VFD status)
    request = bytes([VFD_ADDRESS, 0x03, 0x00, 0x01, 0x00, 0x01])
    request += calculate_crc(request)
    
    print(f"Sending Modbus request: {request.hex(' ')}")
    ser.write(request)
    
    print("Waiting for response...")
    time.sleep(0.1)
    
    response = ser.read(100)
    if response:
        print(f"\n✓ RECEIVED {len(response)} bytes: {response.hex(' ')}")
        print("SUCCESS! VFD is responding!")
    else:
        print("\n✗ No response from VFD")
        print("Check:")
        print("  - VFD is powered on")
        print("  - P308=1 (address)")
        print("  - P310=1 (19200 baud)")
        print("  - P312=2 (Modbus RTU)")
        print("  - Wiring: A-to-A, B-to-B")
    
except KeyboardInterrupt:
    print("\n\nStopped")
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
    for boost in boosters:
        try:
            boost.close()
        except:
            pass
    print("\nAll ports closed")
