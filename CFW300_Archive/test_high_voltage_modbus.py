#!/usr/bin/env python3
import serial
import time
import threading

print("High-voltage Modbus test with continuous carrier")
print("=" * 60)

ser = serial.Serial("/dev/ttyUSB0", 19200, parity="E", stopbits=1, bytesize=8, timeout=1)
ser.rts = True
ser.dtr = True

# Flag to control background thread
keep_running = True

def voltage_keeper():
    """Continuously transmit to maintain voltage"""
    while keep_running:
        try:
            # Transmit filler data to keep voltage up
            ser.write(b'\xFF' * 50)
            time.sleep(0.001)  # Very short delay
        except:
            pass

# Start background thread to maintain voltage
voltage_thread = threading.Thread(target=voltage_keeper, daemon=True)
voltage_thread.start()

print("Background voltage keeper started")
print("Measure voltage now - should be ~1.9V")
time.sleep(2)

# Now try Modbus communication on top of the carrier
print("\nAttempting Modbus read...")

# Read P001
packet = bytes([0x01, 0x03, 0x00, 0x01, 0x00, 0x01, 0xD5, 0xCA])

for attempt in range(5):
    print(f"\nAttempt {attempt + 1}:")
    ser.reset_input_buffer()
    time.sleep(0.05)
    
    # Send Modbus packet
    ser.write(packet)
    print(f"  TX: {packet.hex()}")
    
    # Wait for response
    time.sleep(0.5)
    response = ser.read(100)
    print(f"  RX: {response.hex() if response else 'NONE'} ({len(response)} bytes)")
    
    if response and len(response) >= 7:
        print("  ** SUCCESS! Got valid response **")
        # Parse it
        if response[0] == 0x01 and response[1] == 0x03:
            byte_count = response[2]
            data = response[3:3+byte_count]
            print(f"  Data: {data.hex()}")
            if len(data) == 2:
                value = int.from_bytes(data, byteorder='big')
                print(f"  Value: {value}")
        break
    
    time.sleep(0.5)

keep_running = False
time.sleep(0.1)
ser.close()
print("\nTest complete")
