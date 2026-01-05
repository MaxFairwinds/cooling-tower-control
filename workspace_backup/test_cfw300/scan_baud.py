#!/usr/bin/env python3
from pymodbus.client import ModbusSerialClient
import time

baud_rates = [9600, 19200, 38400, 57600]
device_id = 100

print("Testing different baud rates for device ID 100")
print("=" * 60)

for baud in baud_rates:
    print(f"\nTesting {baud} baud...", end="", flush=True)
    client = ModbusSerialClient(port="/dev/ttyS0", baudrate=baud, timeout=1)
    client.connect()
    
    result = client.read_holding_registers(683, count=1, device_id=device_id)
    if hasattr(result, "isError") and not result.isError():
        print(f" FOUND! Value: {result.registers[0]}")
        print(f"*** CFW300 IS RESPONDING AT {baud} BAUD ***")
        client.close()
        break
    else:
        print(" no response")
    
    client.close()
    time.sleep(0.2)

print("\n" + "=" * 60)
