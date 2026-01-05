#!/usr/bin/env python3
import serial
import time

print("Continuous rapid-fire Modbus test")
print("Measure voltage NOW - this will run continuously")
print("Press Ctrl+C to stop")
print("=" * 60)

ser = serial.Serial("/dev/ttyUSB0", 19200, parity="E", stopbits=1, bytesize=8, timeout=0.1)

# Read P001
packet = bytes([0x01, 0x03, 0x00, 0x01, 0x00, 0x01, 0xD5, 0xCA])

count = 0
responses = {}

try:
    while True:
        ser.reset_input_buffer()
        ser.write(packet)
        time.sleep(0.01)  # Minimal delay - 10ms
        response = ser.read(100)
        
        # Track response patterns
        response_key = response.hex() if response else "NONE"
        responses[response_key] = responses.get(response_key, 0) + 1
        
        count += 1
        if count % 50 == 0:
            print(f"Packets: {count}, Responses: {responses}")
        
except KeyboardInterrupt:
    print(f"\n\nFinal Results:")
    print(f"Total packets sent: {count}")
    print(f"Response breakdown:")
    for resp, cnt in responses.items():
        print(f"  {resp}: {cnt} times ({cnt*100//count}%)")
    ser.close()
