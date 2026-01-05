#!/usr/bin/env python3
from pymodbus.client import ModbusSerialClient

client = ModbusSerialClient(port="/dev/ttyS0", baudrate=9600, timeout=3)
client.connect()

print("Testing P680 (Status Word) - Register 680")
result = client.read_holding_registers(680, count=1, device_id=100)

if hasattr(result, "isError") and not result.isError():
    print(f"SUCCESS! P680 Value: {result.registers[0]} (0x{result.registers[0]:04X})")
else:
    print(f"FAILED: {result}")

client.close()
