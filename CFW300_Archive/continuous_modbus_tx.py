#!/usr/bin/env python3
"""
Continuous Modbus Transmission for Measurement
Sends Modbus requests repeatedly so you can measure voltages with a multimeter.
This will keep the TX line active so you can see differential voltage on A/B.
"""

import serial
import time

def calculate_modbus_crc(data):
    """Calculate Modbus RTU CRC16"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

def create_modbus_request(slave_id, function_code, start_addr, count):
    """Create a Modbus RTU request packet"""
    data = bytearray([
        slave_id,
        function_code,
        (start_addr >> 8) & 0xFF,
        start_addr & 0xFF,
        (count >> 8) & 0xFF,
        count & 0xFF
    ])
    crc = calculate_modbus_crc(data)
    data.append(crc & 0xFF)
    data.append((crc >> 8) & 0xFF)
    return bytes(data)

print("=" * 70)
print("CONTINUOUS MODBUS TRANSMISSION FOR VOLTAGE MEASUREMENT")
print("=" * 70)
print()
print("This script sends Modbus requests continuously (10 per second).")
print("This keeps the RS-485 TX line active so you can measure voltages.")
print()
print("INSTRUCTIONS:")
print("  1. Set multimeter to DC voltage mode")
print("  2. Measure between adapter terminals A and B")
print("  3. You should see voltage fluctuating (typically 2-5V)")
print("  4. If you see 0V, the adapter is not transmitting properly")
print()
print("Press Ctrl+C to stop")
print("=" * 70)
print()

# Open serial port
port = serial.Serial(
    port='/dev/ttyUSB0',
    baudrate=19200,
    bytesize=8,
    parity='E',
    stopbits=1,
    timeout=0.5
)

print(f"Port: {port.name}")
print(f"Baud: {port.baudrate} (19200)")
print(f"Config: 8E1")
print(f"Port open: {port.is_open}")
print()

# Create Modbus request to read P001 (register 1)
slave_id = 1
request = create_modbus_request(slave_id, 0x03, 1, 1)

print(f"Sending to Slave ID: {slave_id}")
print(f"Packet: {' '.join(f'{b:02X}' for b in request)}")
print(f"Packet size: {len(request)} bytes")
print()
print("Starting transmission loop...")
print("-" * 70)

count = 0
start_time = time.time()

try:
    while True:
        # Send Modbus request
        port.write(request)
        port.flush()
        
        count += 1
        
        # Print status every 50 requests
        if count % 50 == 0:
            elapsed = time.time() - start_time
            rate = count / elapsed
            print(f"Sent {count} requests ({rate:.1f}/sec) - TXD should be blinking")
        
        # Wait 100ms between requests (10 requests/sec)
        time.sleep(0.1)
        
        # Clear any received data (shouldn't get any, but just in case)
        if port.in_waiting > 0:
            received = port.read(port.in_waiting)
            print(f"\n✓ RECEIVED {len(received)} bytes: {' '.join(f'{b:02X}' for b in received)}")
        
except KeyboardInterrupt:
    print()
    print("-" * 70)
    print(f"\nStopped after {count} requests")
    elapsed = time.time() - start_time
    print(f"Runtime: {elapsed:.1f} seconds")
    print(f"Average rate: {count/elapsed:.1f} requests/second")
    
finally:
    port.close()
    print("\nPort closed")
    print("=" * 70)
