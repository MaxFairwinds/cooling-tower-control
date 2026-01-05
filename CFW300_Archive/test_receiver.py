#!/usr/bin/env python3
"""
Test RS485 receiver by monitoring incoming data.
Apply external voltage to A-B terminals:
- Connect battery + to A terminal
- Connect battery - to B terminal
- 1.5V should trigger receiver and we should see data
"""

import serial
import time

PORT = '/dev/cu.usbserial-1420'
BAUD = 19200

print("RS485 Receiver Test")
print("=" * 60)
print("Instructions:")
print("1. Connect a 1.5V battery:")
print("   - Battery + (positive) to A terminal")
print("   - Battery - (negative) to B terminal")
print()
print("2. If receiver works, we should see:")
print("   - RXD LED lights up")
print("   - Data appears below")
print()
print("Press Ctrl+C to stop")
print("=" * 60)
print()

try:
    ser = serial.Serial(
        port=PORT,
        baudrate=BAUD,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_EVEN,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.1
    )
    
    # Ensure receiver is enabled (RE=LOW)
    ser.rts = False  # RE should be LOW to enable receiver
    ser.dtr = False
    
    print(f"Opened {PORT}")
    print(f"RTS: {ser.rts} (RE enabled)")
    print()
    print("Monitoring for incoming data...")
    print("Connect battery to A-B now...")
    print()
    
    byte_count = 0
    start = time.time()
    
    while True:
        data = ser.read(100)  # Read up to 100 bytes
        if data:
            byte_count += len(data)
            print(f"[{time.time()-start:.1f}s] Received {len(data)} bytes: {data.hex(' ')}")
            print(f"  ASCII: {data}")
        
        time.sleep(0.1)
        
        # Print status every 5 seconds
        if int(time.time() - start) % 5 == 0 and (time.time() - start) > 0.1:
            if byte_count == 0:
                print(f"[{time.time()-start:.1f}s] No data yet - is battery connected?")
            time.sleep(1)

except KeyboardInterrupt:
    print(f"\n\nStopped - received {byte_count} total bytes")
    
except Exception as e:
    print(f"\nError: {e}")
    
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Port closed")
