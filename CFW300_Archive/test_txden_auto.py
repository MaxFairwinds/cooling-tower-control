#!/usr/bin/env python3
"""
Test RS485 with CBUS0=TXDEN for hardware automatic direction control.
This should work WITHOUT setting RTS/DTR.
"""

import serial
import time

PORT = '/dev/cu.usbserial-1420'
BAUD = 19200

print("Testing Hardware Automatic Direction Control")
print("=" * 60)
print("CBUS0 now set to TXDEN - should enable RS485 automatically")
print("Testing WITHOUT RTS/DTR control")
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
    
    # Leave RTS and DTR at default (should be LOW)
    print(f"Port: {PORT}")
    print(f"RTS: {ser.rts} (not controlling)")
    print(f"DTR: {ser.dtr} (not controlling)")
    print()
    print("Transmitting 0xAA continuously...")
    print("Measure A-B voltage - should be 1.5-5V now!")
    print()
    print("Press Ctrl+C to stop")
    print()
    
    byte_count = 0
    start = time.time()
    
    while True:
        ser.write(b'\xAA' * 10)
        byte_count += 10
        
        if byte_count % 500 == 0:
            elapsed = time.time() - start
            print(f"Sent {byte_count} bytes | {elapsed:.1f}s | A-B voltage = ?")
        
        time.sleep(0.02)

except KeyboardInterrupt:
    print("\n\nStopped - what voltage did you measure?")
    
except Exception as e:
    print(f"Error: {e}")
    
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Port closed")
