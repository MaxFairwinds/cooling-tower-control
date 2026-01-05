#!/usr/bin/env python3
from pymodbus.client import ModbusSerialClient
import time

client = ModbusSerialClient(port="/dev/ttyS0", baudrate=9600, timeout=1)
client.connect()

print("Testing device IDs: 1, 100, 101, 247")
for device_id in [1, 100, 101, 247]:
    print(f"ID {device_id}...", end="", flush=True)
    result = client.read_holding_registers(683, count=1, device_id=device_id)
    if hasattr(result, "isError") and not result.isError():
        print(f" FOUND! Value: {result.registers[0]}")
    else:
        print(" no response")
    time.sleep(0.1)

client.close()
