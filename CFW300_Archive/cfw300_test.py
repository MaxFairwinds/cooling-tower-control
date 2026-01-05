#!/usr/bin/env python3
"""
CFW300 VFD Communication Script
Using Modbus RTU over RS485
"""

import serial
import time
import struct

class CFW300:
    def __init__(self, port='/dev/ttyUSB0', slave_address=1, baudrate=9600):
        """
        Initialize CFW300 VFD connection
        
        Default settings for CFW300:
        - Baud rate: 9600
        - Data bits: 8
        - Parity: Even (E)
        - Stop bits: 1
        - Slave address: 1
        """
        self.port = port
        self.slave_address = slave_address
        self.serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            timeout=1
        )
        print(f"Connected to {port} at {baudrate} baud, 8E1")
    
    def calculate_crc(self, data):
        """Calculate Modbus RTU CRC16"""
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x0001:
                    crc >>= 1
                    crc ^= 0xA001
                else:
                    crc >>= 1
        return crc
    
    def read_holding_register(self, register_address, num_registers=1):
        """
        Read holding register(s) using Modbus function code 0x03
        """
        # Build Modbus RTU request
        request = bytearray([
            self.slave_address,  # Slave address
            0x03,                # Function code: Read Holding Registers
            (register_address >> 8) & 0xFF,  # Register address high byte
            register_address & 0xFF,          # Register address low byte
            (num_registers >> 8) & 0xFF,     # Number of registers high byte
            num_registers & 0xFF              # Number of registers low byte
        ])
        
        # Add CRC
        crc = self.calculate_crc(request)
        request.append(crc & 0xFF)
        request.append((crc >> 8) & 0xFF)
        
        # Clear buffer and send request
        self.serial.reset_input_buffer()
        self.serial.write(request)
        
        # Read response
        time.sleep(0.1)
        response = self.serial.read(100)
        
        if len(response) < 5:
            print(f"Error: Response too short ({len(response)} bytes)")
            return None
        
        # Verify CRC
        received_crc = response[-2] | (response[-1] << 8)
        calculated_crc = self.calculate_crc(response[:-2])
        
        if received_crc != calculated_crc:
            print("Error: CRC mismatch")
            return None
        
        # Extract data
        byte_count = response[2]
        data = response[3:3+byte_count]
        
        # Convert to register values
        registers = []
        for i in range(0, len(data), 2):
            reg_value = (data[i] << 8) | data[i+1]
            registers.append(reg_value)
        
        return registers[0] if num_registers == 1 else registers
    
    def write_holding_register(self, register_address, value):
        """
        Write single holding register using Modbus function code 0x06
        """
        # Build Modbus RTU request
        request = bytearray([
            self.slave_address,  # Slave address
            0x06,                # Function code: Write Single Register
            (register_address >> 8) & 0xFF,  # Register address high byte
            register_address & 0xFF,          # Register address low byte
            (value >> 8) & 0xFF,             # Value high byte
            value & 0xFF                      # Value low byte
        ])
        
        # Add CRC
        crc = self.calculate_crc(request)
        request.append(crc & 0xFF)
        request.append((crc >> 8) & 0xFF)
        
        # Clear buffer and send request
        self.serial.reset_input_buffer()
        self.serial.write(request)
        
        # Read response
        time.sleep(0.1)
        response = self.serial.read(100)
        
        if len(response) < 8:
            print(f"Error: Response too short ({len(response)} bytes)")
            return False
        
        # Verify CRC
        received_crc = response[-2] | (response[-1] << 8)
        calculated_crc = self.calculate_crc(response[:-2])
        
        if received_crc != calculated_crc:
            print("Error: CRC mismatch")
            return False
        
        return True
    
    def close(self):
        """Close serial connection"""
        self.serial.close()


def main():
    print("CFW300 VFD Test Script")
    print("=" * 50)
    
    # Create VFD instance
    vfd = CFW300(port='/dev/ttyUSB0', slave_address=1, baudrate=9600)
    
    try:
        # Test: Read parameter P0001 (common parameter)
        print("\n1. Reading test register...")
        result = vfd.read_holding_register(1)
        if result is not None:
            print(f"   Register 1 value: {result}")
        else:
            print("   Failed to read register")
        
        # Test: Read multiple registers
        print("\n2. Reading multiple registers (1-3)...")
        result = vfd.read_holding_register(1, 3)
        if result is not None:
            print(f"   Registers: {result}")
        else:
            print("   Failed to read registers")
        
        print("\n" + "=" * 50)
        print("Test complete!")
        print("\nNote: If you get errors, check:")
        print("  - RS485 wiring (A to A, B to B)")
        print("  - VFD slave address (default is 1)")
        print("  - VFD baud rate (try 9600, 19200, or 38400)")
        print("  - VFD communication protocol enabled")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        vfd.close()


if __name__ == "__main__":
    main()
