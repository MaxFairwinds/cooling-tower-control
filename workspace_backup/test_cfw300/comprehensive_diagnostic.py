#!/usr/bin/env python3
"""
Comprehensive CFW300 Diagnostic
Tests raw serial communication and Modbus at multiple levels
"""

import serial
import time
from pymodbus.client import ModbusSerialClient

print("="*70)
print("CFW300 COMPREHENSIVE DIAGNOSTIC")
print("="*70)

# Test 1: Raw Serial Port Access
print("\n[TEST 1] Raw Serial Port Access")
print("-" * 70)
try:
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
    print("✓ Serial port opened successfully")
    print(f"  Port: {ser.port}")
    print(f"  Baudrate: {ser.baudrate}")
    print(f"  Timeout: {ser.timeout}s")
    ser.close()
except Exception as e:
    print(f"✗ Failed to open serial port: {e}")
    exit(1)

# Test 2: Pymodbus Client Creation
print("\n[TEST 2] Pymodbus Client Creation")
print("-" * 70)
try:
    client = ModbusSerialClient(
        port='/dev/ttyS0',
        baudrate=9600,
        bytesize=8,
        parity='N',
        stopbits=1,
        timeout=3
    )
    print("✓ Modbus client created")
except Exception as e:
    print(f"✗ Failed to create Modbus client: {e}")
    exit(1)

# Test 3: Connect to Modbus
print("\n[TEST 3] Modbus Connection")
print("-" * 70)
if client.connect():
    print("✓ Modbus client connected")
else:
    print("✗ Failed to connect Modbus client")
    exit(1)

# Test 4: Try multiple device IDs
print("\n[TEST 4] Scanning Device IDs")
print("-" * 70)
device_ids_to_test = [1, 100, 101, 247]
found_devices = []

for device_id in device_ids_to_test:
    print(f"Testing ID {device_id}...", end=" ", flush=True)
    try:
        # Try to read P683 (status word) - register 683
        result = client.read_holding_registers(683, count=1, device_id=device_id)
        if not result.isError():
            print(f"✓ FOUND! Value: {result.registers[0]}")
            found_devices.append(device_id)
        else:
            print(f"✗ Error: {result}")
    except Exception as e:
        print(f"✗ Exception: {e}")

# Test 5: Try reading different registers on ID 100
print("\n[TEST 5] Register Scan on Device ID 100")
print("-" * 70)
registers_to_test = [
    (683, "P683 - Status Word"),
    (681, "P681 - Speed Reference"),
    (682, "P682 - Control Word"),
    (48, "P048 - Fault Code"),
    (220, "P220 - Command Source"),
    (221, "P221 - Speed Source"),
    (308, "P308 - RS485 Address"),
    (310, "P310 - Baud Rate"),
]

for reg, desc in registers_to_test:
    print(f"Reading {desc} (reg {reg})...", end=" ", flush=True)
    try:
        result = client.read_holding_registers(reg, count=1, device_id=100)
        if not result.isError():
            print(f"✓ Value: {result.registers[0]}")
        else:
            print(f"✗ Error: {result}")
    except Exception as e:
        print(f"✗ Exception: {e}")

client.close()

# Summary
print("\n" + "="*70)
print("DIAGNOSTIC SUMMARY")
print("="*70)
if found_devices:
    print(f"✓ Found {len(found_devices)} device(s): {found_devices}")
else:
    print("✗ NO DEVICES FOUND")
    print("\nPossible Issues:")
    print("  1. CFW300 not configured for Modbus (P220/P221 must be 5)")
    print("  2. Wrong baud rate (verify P310=0 for 9600)")
    print("  3. RS-485 wiring issue (try original polarity)")
    print("  4. CFW300 may need power cycle")
    print("  5. Check for termination resistor requirement")
print("="*70)
