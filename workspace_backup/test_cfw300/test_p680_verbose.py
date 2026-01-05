#!/usr/bin/env python3
import sys
print("Starting P680 Test...", flush=True)

try:
    from pymodbus.client import ModbusSerialClient
    import logging
    logging.basicConfig()
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    print("Imported pymodbus and enabled logging", flush=True)
except ImportError as e:
    print(f"Failed to import pymodbus: {e}", flush=True)
    sys.exit(1)

try:
    # Setup serial client
    # For Waveshare RS485 CAN HAT (B), use /dev/ttySC1 (Channel 2?)
    client = ModbusSerialClient(port="/dev/ttySC1", baudrate=9600, timeout=2)
    print("Created client", flush=True)
    
    if client.connect():
        print("Connected to serial port", flush=True)
    else:
        print("Failed to connect to serial port", flush=True)
        sys.exit(1)

    print("Attempting to read P680 (Register 680) from Device ID 100...", flush=True)
    result = client.read_holding_registers(680, count=1, device_id=100)

    print(f"Raw Result Type: {type(result)}", flush=True)
    
    if hasattr(result, "isError") and result.isError():
        print(f"Modbus Error: {result}", flush=True)
    elif hasattr(result, "registers"):
        print(f"SUCCESS! P680 Value: {result.registers[0]} (0x{result.registers[0]:04X})", flush=True)
    else:
        print(f"Unexpected result: {result}", flush=True)

    client.close()
    print("Done.", flush=True)

except Exception as e:
    print(f"An exception occurred: {e}", flush=True)
