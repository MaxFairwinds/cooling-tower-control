#!/usr/bin/env python3
"""
Test RS485 using pyserial's RS485 mode configuration.
This uses the proper RS485 settings that might enable the transceiver correctly.
"""

import serial
from serial.rs485 import RS485Settings
import time

PORT = '/dev/cu.usbserial-1420'
BAUD = 19200

print("RS485 Test with Proper RS485 Mode")
print("=" * 50)
print("Using pyserial RS485Settings")
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
    
    # Configure RS485 mode with proper settings
    rs485_settings = RS485Settings(
        rts_level_for_tx=True,      # RTS=HIGH when transmitting
        rts_level_for_rx=False,     # RTS=LOW when receiving
        loopback=False,
        delay_before_tx=0,          # No delay before TX
        delay_before_rx=0           # No delay before RX
    )
    
    ser.rs485_mode = rs485_settings
    
    print(f"Opened {PORT}")
    print(f"RS485 mode enabled:")
    print(f"  RTS for TX: {rs485_settings.rts_level_for_tx}")
    print(f"  RTS for RX: {rs485_settings.rts_level_for_rx}")
    print()
    print("Transmitting 0xAA continuously...")
    print("Measure A-B voltage now!")
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
            print(f"Sent {byte_count} bytes | {elapsed:.1f}s | What voltage?")
        
        time.sleep(0.02)

except KeyboardInterrupt:
    print("\n\nStopped")
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Port closed")
