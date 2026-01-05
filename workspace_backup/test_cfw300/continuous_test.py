#!/usr/bin/env python3
"""
Continuously send Modbus commands for voltmeter testing.
This will cause the RS-485 lines to fluctuate so you can measure with a voltmeter.
"""
from pymodbus.client import ModbusSerialClient
import time

print("Starting continuous Modbus transmission...")
print("Measure voltage between A and B on the Waveshare HAT")
print("You should see voltage fluctuating between -5V and +5V")
print("Press Ctrl+C to stop")
print()

client = ModbusSerialClient(port="/dev/ttyAMA0", baudrate=9600, timeout=0.5)
client.connect()

count = 0
try:
    while True:
        # Send a read request
        result = client.read_holding_registers(680, count=1, device_id=100)
        count += 1
        
        if count % 10 == 0:
            print(f"Sent {count} requests... (voltage should be fluctuating)")
        
        time.sleep(0.1)  # 10 requests per second
        
except KeyboardInterrupt:
    print("\nStopped.")
    client.close()
