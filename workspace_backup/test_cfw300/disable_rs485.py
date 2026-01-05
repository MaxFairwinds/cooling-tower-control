#!/usr/bin/env python3
"""
Disable RS-485 mode on the UART using Linux kernel ioctl.
Restores standard serial mode.
"""
import fcntl
import struct
import serial

# RS-485 ioctl constants
TIOCSRS485 = 0x542F

def disable_rs485(port_path):
    """Disable RS-485 mode on the specified serial port."""
    print(f"Disabling RS-485 mode on {port_path}...")
    
    ser = serial.Serial(port_path, baudrate=9600, timeout=1)
    
    # Set flags to 0 to disable RS-485 mode
    # struct serial_rs485 { flags, delay_before, delay_after, padding[5] }
    rs485_config = struct.pack('I' * 7, 0, 0, 0, 0, 0, 0, 0)
    
    try:
        fcntl.ioctl(ser.fileno(), TIOCSRS485, rs485_config)
        print("✓ RS-485 mode disabled (Standard Serial Mode)")
        return True
    except Exception as e:
        print(f"✗ Failed to disable RS-485 mode: {e}")
        return False
    finally:
        ser.close()

if __name__ == "__main__":
    disable_rs485("/dev/ttyAMA0")
