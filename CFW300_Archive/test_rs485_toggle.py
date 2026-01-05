#!/usr/bin/env python3
"""
Toggle RTS and DTR to find the best RS485 enable signal.
This will cycle through different control line combinations.
"""

import serial
import time

PORT = '/dev/cu.usbserial-1420'
BAUD = 19200

print("RS485 Control Line Test")
print("=" * 50)
print("This will test different RTS/DTR combinations")
print("Watch your multimeter voltage on A-B terminals")
print()
print("Press Ctrl+C to stop")
print("=" * 50)
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
    
    print(f"Opened {PORT}\n")
    
    tests = [
        ("RTS=LOW, DTR=LOW", False, False),
        ("RTS=HIGH, DTR=LOW", True, False),
        ("RTS=LOW, DTR=HIGH", False, True),
        ("RTS=HIGH, DTR=HIGH", True, True),
    ]
    
    cycle = 0
    while True:
        for test_name, rts_state, dtr_state in tests:
            cycle += 1
            print(f"\nCycle {cycle}: {test_name}")
            print("-" * 40)
            
            ser.rts = rts_state
            ser.dtr = dtr_state
            time.sleep(0.1)
            
            print(f"Set RTS={ser.rts}, DTR={ser.dtr}")
            print("Transmitting for 3 seconds...")
            
            start = time.time()
            byte_count = 0
            while time.time() - start < 3.0:
                ser.write(b'\xAA' * 10)
                byte_count += 10
                time.sleep(0.02)
            
            print(f"Sent {byte_count} bytes")
            print("What voltage do you see?")
            time.sleep(1)  # Pause to read meter
        
        print("\n" + "=" * 50)
        print("Repeating cycle...\n")

except KeyboardInterrupt:
    print("\n\nStopped by user")
    print("\nBased on voltage readings, which combination gave highest voltage?")
    
except Exception as e:
    print(f"\nError: {e}")
    
finally:
    if 'ser' in locals() and ser.is_open:
        ser.rts = False
        ser.dtr = False
        ser.close()
        print("Serial port closed")
