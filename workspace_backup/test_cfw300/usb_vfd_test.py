#!/usr/bin/env python3
"""
CFW300 VFD Test Script - USB-RS485 Adapter
Tests Modbus RTU communication with WEG CFW300 VFD
"""
import sys
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException
import time

# CFW300 Configuration
VFD_SLAVE_ID = 1  # P308
VFD_PORT = '/dev/ttyUSB0'
VFD_BAUDRATE = 19200  # P310 = 1 (19200 baud)
VFD_PARITY = 'E'  # P311 = 1 (Even parity)
VFD_STOPBITS = 1
VFD_BYTESIZE = 8

print("=" * 60)
print("CFW300 VFD CONNECTION TEST")
print("=" * 60)
print(f"Port: {VFD_PORT}")
print(f"Baud Rate: {VFD_BAUDRATE}")
print(f"Slave ID: {VFD_SLAVE_ID}")
print(f"Parity: {VFD_PARITY}")
print()

try:
    # Create Modbus RTU client
    client = ModbusSerialClient(
        port=VFD_PORT,
        baudrate=VFD_BAUDRATE,
        parity=VFD_PARITY,
        stopbits=VFD_STOPBITS,
        bytesize=VFD_BYTESIZE,
        timeout=1
    )
    
    print("Connecting to VFD...")
    if not client.connect():
        print("✗ FAILED: Could not open serial port")
        sys.exit(1)
    
    print("✓ Serial port opened")
    print()
    
    # Test 1: Read P680 (Status Word)
    print("Test 1: Reading P680 (Status Word)...")
    try:
        # In pymodbus 3.x, slave ID is passed separately
        result = client.read_holding_registers(680, count=1, device_id=VFD_SLAVE_ID)
        if result.isError():
            print(f"✗ FAILED: {result}")
        else:
            status = result.registers[0]
            print(f"✓ SUCCESS: P680 = {status} (0x{status:04X})")
            print(f"  Motor Running: {'Yes' if status & 0x01 else 'No'}")
            print(f"  Direction: {'Reverse' if status & 0x02 else 'Forward'}")
            print(f"  Fault: {'Yes' if status & 0x08 else 'No'}")
    except Exception as e:
        print(f"✗ EXCEPTION: {e}")
    
    print()
    
    # Test 2: Read P002 (Motor Speed Reference)
    print("Test 2: Reading P002 (Motor Speed Reference)...")
    try:
        result = client.read_holding_registers(2, count=1, device_id=VFD_SLAVE_ID)
        if result.isError():
            print(f"✗ FAILED: {result}")
        else:
            speed_ref = result.registers[0] / 10.0  # P002 is in 0.1 Hz
            print(f"✓ SUCCESS: P002 = {speed_ref:.1f} Hz")
    except Exception as e:
        print(f"✗ EXCEPTION: {e}")
    
    print()
    
    # Test 3: Read P001 (Motor Rated Speed)
    print("Test 3: Reading P001 (Motor Rated Speed)...")
    try:
        result = client.read_holding_registers(1, count=1, device_id=VFD_SLAVE_ID)
        if result.isError():
            print(f"✗ FAILED: {result}")
        else:
            rated_speed = result.registers[0] / 10.0
            print(f"✓ SUCCESS: P001 = {rated_speed:.1f} Hz")
    except Exception as e:
        print(f"✗ EXCEPTION: {e}")
    
    print()
    print("=" * 60)
    
    client.close()
    
except Exception as e:
    print(f"\n✗ FATAL ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
