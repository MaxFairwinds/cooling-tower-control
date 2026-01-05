#!/usr/bin/env python3
"""
Maximize RS485 transmit voltage by driving all control signals aggressively.
Based on observation that multiple scripts increased voltage.
"""

import serial
import time
import threading

PORT = '/dev/cu.usbserial-1420'
BAUD = 19200

print("Maximum Drive Test - Aggressive TX")
print("=" * 60)
print("This will:")
print("- Set RTS=HIGH, DTR=HIGH")
print("- Continuously transmit at maximum rate")
print("- Use aggressive buffering")
print()
print("Measure A-B voltage - should be HIGHER than 0.14V")
print("Press Ctrl+C to stop")
print("=" * 60)
print()

stop_flag = False

def transmit_thread(ser):
    """Transmit continuously in separate thread"""
    byte_count = 0
    while not stop_flag:
        # Send large blocks continuously
        ser.write(b'\xFF' * 100)  # 100 bytes of HIGH
        byte_count += 100
        if byte_count % 10000 == 0:
            print(f"Sent {byte_count} bytes...")

try:
    ser = serial.Serial(
        port=PORT,
        baudrate=BAUD,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_EVEN,
        stopbits=serial.STOPBITS_ONE,
        timeout=0,  # Non-blocking
        write_timeout=0
    )
    
    # Maximize control signals
    ser.rts = True
    ser.dtr = True
    
    print(f"Port: {PORT}")
    print(f"RTS: {ser.rts} (forced HIGH)")
    print(f"DTR: {ser.dtr} (forced HIGH)")
    print()
    print("Starting aggressive transmission...")
    print()
    
    # Start transmission thread
    t = threading.Thread(target=transmit_thread, args=(ser,), daemon=True)
    t.start()
    
    # Monitor for 30 seconds
    for i in range(30):
        print(f"[{i+1}s] Transmitting at maximum rate - what voltage do you see?")
        time.sleep(1)
    
    print("\nMeasured voltage = ?")

except KeyboardInterrupt:
    print("\n\nStopped")
    
except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
    
finally:
    stop_flag = True
    time.sleep(0.2)
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Port closed")
