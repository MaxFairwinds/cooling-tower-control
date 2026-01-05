#!/usr/bin/env python3
"""
RS-485 Loopback Test with Explicit RS-485 Mode Enabled
For Waveshare RS485 CAN HAT (B) which has two channels.
"""
import serial
import time
import struct
import fcntl
import termios

# RS-485 ioctl constants
TIOCSRS485 = 0x542F
TIOCGRS485 = 0x542E
SER_RS485_ENABLED = 0x01
SER_RS485_RTS_ON_SEND = 0x02
SER_RS485_RTS_AFTER_SEND = 0x04
SER_RS485_RX_DURING_TX = 0x10

def enable_rs485(fd):
    """Enable RS-485 mode via ioctl"""
    # struct serial_rs485 { __u32 flags; __u32 delay_rts_before_send; __u32 delay_rts_after_send; ... }
    flags = SER_RS485_ENABLED | SER_RS485_RTS_ON_SEND
    rs485_struct = struct.pack('IIII', flags, 0, 0, 0) + (b'\x00' * 20)  # Padding
    try:
        fcntl.ioctl(fd, TIOCSRS485, rs485_struct)
        print(f"  RS-485 mode enabled on fd {fd}")
        return True
    except Exception as e:
        print(f"  RS-485 ioctl failed: {e}")
        return False

print("=" * 60)
print("RS-485 LOOPBACK TEST (With Explicit RS-485 Mode)")
print("=" * 60)
print()
print("INSTRUCTIONS:")
print("1. Connect Channel 0 'A' to Channel 1 'A'")
print("2. Connect Channel 0 'B' to Channel 1 'B'")
print()

try:
    # Open both ports
    port0 = serial.Serial("/dev/ttySC0", baudrate=9600, timeout=2)
    port1 = serial.Serial("/dev/ttySC1", baudrate=9600, timeout=2)
    
    print(f"Opened {port0.port} and {port1.port}")
    
    # Enable RS-485 mode on both ports
    print("Enabling RS-485 mode...")
    enable_rs485(port0.fileno())
    enable_rs485(port1.fileno())
    print()

    # Clear any pending data
    port0.reset_input_buffer()
    port1.reset_input_buffer()

    # Test 1: Port 0 -> Port 1
    msg1 = b"HELLO_FROM_0"
    print(f"Sending from {port0.port}: {msg1}")
    port0.write(msg1)
    port0.flush()
    time.sleep(0.2)
    
    recv1 = port1.read(len(msg1))
    print(f"Received on {port1.port}:  {recv1}")
    
    if msg1 == recv1:
        print("✓ PASS: Port 0 -> Port 1")
    elif recv1 == b'':
        print("✗ FAIL: No data received (timeout)")
    else:
        print("✗ FAIL: Port 0 -> Port 1 (data mismatch)")
    print()

    # Test 2: Port 1 -> Port 0
    msg2 = b"HELLO_FROM_1"
    print(f"Sending from {port1.port}: {msg2}")
    port1.write(msg2)
    port1.flush()
    time.sleep(0.2)
    
    recv2 = port0.read(len(msg2))
    print(f"Received on {port0.port}:  {recv2}")
    
    if msg2 == recv2:
        print("✓ PASS: Port 1 -> Port 0")
    elif recv2 == b'':
        print("✗ FAIL: No data received (timeout)")
    else:
        print("✗ FAIL: Port 1 -> Port 0 (data mismatch)")

    port0.close()
    port1.close()

except Exception as e:
    print(f"\nERROR: {e}")

print()
print("=" * 60)
