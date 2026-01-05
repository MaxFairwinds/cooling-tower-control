#!/usr/bin/env python3
"""Test script to determine correct pymodbus API usage"""
from pymodbus.client import ModbusSerialClient

# Create client
client = ModbusSerialClient(
    port='/dev/ttyS0',
    baudrate=9600,
    parity='N',
    stopbits=1,
    bytesize=8,
    timeout=1
)

# Try to connect (will fail without hardware, but that's OK)
try:
    client.connect()
except Exception as e:
    print(f"Connect failed (expected): {e}")

# Test write_register - try different approaches
print("\nTesting write_register API...")
try:
    # Approach 1: slave as keyword
    result = client.write_register(0x2000, 1, slave=1)
    print("✓ slave=1 works")
except TypeError as e:
    print(f"✗ slave=1 failed: {e}")

try:
    # Approach 2: unit as keyword  
    result = client.write_register(0x2000, 1, unit=1)
    print("✓ unit=1 works")
except TypeError as e:
    print(f"✗ unit=1 failed: {e}")

# Check method signature
import inspect
sig = inspect.signature(client.write_register)
print(f"\nActual signature: {sig}")
