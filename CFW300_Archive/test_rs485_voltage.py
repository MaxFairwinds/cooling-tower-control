#!/usr/bin/env python3
"""
Test RS485 voltage differential output.
Continuously transmits data to produce measurable voltage on A-B terminals.
"""

import serial
import time

# Serial port configuration
PORT = '/dev/cu.usbserial-1420'
BAUD = 19200

print("RS485 Voltage Differential Test")
print("=" * 50)
print(f"Port: {PORT}")
print(f"Baud rate: {BAUD}")
print()
print("This script will continuously transmit data.")
print("Measure voltage between A and B terminals with multimeter.")
print()
print("Expected: 2-5V differential when transmitting")
print("          ~0V when idle")
print()
print("Press Ctrl+C to stop")
print("=" * 50)
print()

try:
    # Open serial port
    ser = serial.Serial(
        port=PORT,
        baudrate=BAUD,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_EVEN,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.1
    )
    
    # Set RTS/DTR states
    ser.rts = False
    ser.dtr = False
    
    print(f"Opened {PORT}")
    print(f"RTS: {ser.rts}, DTR: {ser.dtr}")
    print()
    
    # Test 1: Continuous transmission with RTS LOW
    print("TEST 1: Transmitting with RTS=LOW (hardware auto-control)")
    print("Sending 0xAA (alternating bits) continuously...")
    print("Measure A-B voltage now!")
    print()
    
    packet_count = 0
    start_time = time.time()
    
    while True:
        # Send alternating bit pattern for clear signal
        ser.write(b'\xAA' * 10)  # 10 bytes of 0xAA
        packet_count += 1
        
        # Print status every second
        if packet_count % 50 == 0:
            elapsed = time.time() - start_time
            print(f"Sent {packet_count} packets ({packet_count * 10} bytes) in {elapsed:.1f}s")
        
        time.sleep(0.02)  # Small delay between packets

except KeyboardInterrupt:
    print("\n\nStopped by user")
    
except Exception as e:
    print(f"\nError: {e}")
    
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial port closed")
