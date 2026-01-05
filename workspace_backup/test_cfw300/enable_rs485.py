#!/usr/bin/env python3
"""
Enable RS-485 mode on the UART using Linux kernel ioctl.
This is REQUIRED for the Waveshare HAT to transmit properly.
"""
import fcntl
import struct
import serial

# RS-485 ioctl constants
TIOCSRS485 = 0x542F

# RS-485 flags
SER_RS485_ENABLED = (1 << 0)
SER_RS485_RTS_ON_SEND = (1 << 1)
SER_RS485_RTS_AFTER_SEND = (1 << 2)

def enable_rs485(port_path):
    """Enable RS-485 mode on the specified serial port."""
    print(f"Enabling RS-485 mode on {port_path}...")
    
    # Open the serial port
    ser = serial.Serial(port_path, baudrate=9600, timeout=1)
    
    # Create RS-485 configuration structure
    # struct serial_rs485 {
    #     __u32 flags;
    #     __u32 delay_rts_before_send;
    #     __u32 delay_rts_after_send;
    #     __u32 padding[5];
    # }
    
    flags = SER_RS485_ENABLED | SER_RS485_RTS_ON_SEND
    delay_before = 0  # milliseconds
    delay_after = 0   # milliseconds
    
    # Pack the structure (7 u32 values)
    rs485_config = struct.pack('I' * 7, flags, delay_before, delay_after, 0, 0, 0, 0)
    
    # Apply RS-485 configuration
    try:
        fcntl.ioctl(ser.fileno(), TIOCSRS485, rs485_config)
        print("✓ RS-485 mode enabled successfully!")
        print(f"  Flags: 0x{flags:08X}")
        print(f"  RTS will be HIGH during transmission")
        return True
    except Exception as e:
        print(f"✗ Failed to enable RS-485 mode: {e}")
        return False
    finally:
        ser.close()

if __name__ == "__main__":
    enable_rs485("/dev/ttyAMA0")
