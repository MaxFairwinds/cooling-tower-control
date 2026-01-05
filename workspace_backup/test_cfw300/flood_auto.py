#!/usr/bin/env python3
"""
RS-485 Flood Test - Automatic Mode (ioctl)
Continuously sends data on Channel 0 using kernel RS-485 driver.
"""
import serial
import time
import struct
import fcntl

# RS-485 ioctl constants
TIOCSRS485 = 0x542F
SER_RS485_ENABLED = 0x01
SER_RS485_RTS_ON_SEND = 0x02

def enable_rs485(fd):
    flags = SER_RS485_ENABLED | SER_RS485_RTS_ON_SEND
    rs485_struct = struct.pack('IIII', flags, 0, 0, 0) + (b'\x00' * 20)
    try:
        fcntl.ioctl(fd, TIOCSRS485, rs485_struct)
        print(f"RS-485 mode enabled on fd {fd}")
        return True
    except Exception as e:
        print(f"RS-485 ioctl failed: {e}")
        return False

print("=" * 60)
print("RS-485 FLOOD TEST (Automatic Mode)")
print("=" * 60)
print("Sending 'U' (0x55) continuously on /dev/ttySC0...")
print("Measure voltage between A and B on Channel 0.")
print("Press Ctrl+C to stop.")
print()

try:
    port0 = serial.Serial("/dev/ttySC0", baudrate=9600, timeout=1)
    
    if enable_rs485(port0.fileno()):
        print("Driver configured for Auto-Direction.")
    else:
        print("Failed to configure driver.")

    while True:
        port0.write(b'U' * 50)
        # port0.flush() # Don't flush, just keep filling buffer
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\nStopped.")
    port0.close()
except Exception as e:
    print(f"\nERROR: {e}")
