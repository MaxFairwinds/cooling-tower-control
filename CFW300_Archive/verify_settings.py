#!/usr/bin/env python3
"""Quick verification of key VFD parameters and Modbus responses"""
import serial
import time
import struct

def crc16(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return struct.pack('<H', crc)

def read_param(ser, param_num):
    """Read VFD parameter"""
    msg = bytes([1, 3, 0, param_num-1, 0, 1]) + crc16(bytes([1, 3, 0, param_num-1, 0, 1]))
    ser.reset_input_buffer()
    ser.write(msg)
    ser.flush()
    time.sleep(0.1)
    return ser.read(100)

print("VFD Parameter Verification")
print("="*50)

ser = serial.Serial('/dev/ttyUSB0', 19200, parity='E', timeout=0.5)
time.sleep(0.5)

# Key parameters to verify
params = [
    (1, "P001", None),
    (202, "P202", 3),
    (220, "P220", 6),
    (308, "P308", 1),
    (310, "P310", 1),
    (311, "P311", 1),
    (312, "P312", 2),
    (316, "P316", 0),
]

for num, name, expected in params:
    resp = read_param(ser, num)
    print(f"\n{name}:")
    print(f"  TX: 01 03 {(num-1)>>8:02X} {(num-1)&0xFF:02X} 00 01 [CRC]")
    print(f"  RX ({len(resp)}): {' '.join(f'{b:02X}' for b in resp) if resp else 'NONE'}")
    
    if len(resp) == 7:
        value = (resp[3] << 8) | resp[4]
        print(f"  Value: {value}", end="")
        if expected is not None:
            print(f" (expected {expected}) {'✓' if value == expected else '✗ MISMATCH'}")
        else:
            print()
    elif len(resp) > 0:
        print(f"  ✗ Invalid response length")
    else:
        print(f"  ✗ No response")
    
    time.sleep(0.2)

ser.close()
