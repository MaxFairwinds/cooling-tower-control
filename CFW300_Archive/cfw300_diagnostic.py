#!/usr/bin/env python3
"""
CFW300 VFD Diagnostic Script
Tests different baud rates and configurations
"""

import serial
import time

def calculate_crc(data):
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

def test_modbus_connection(port, baudrate, parity, slave_address=1):
    """Test Modbus connection with given parameters"""
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=parity,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.5
        )
        
        # Build request to read register 0 (often contains basic info)
        request = bytearray([
            slave_address,  # Slave address
            0x03,          # Function code: Read Holding Registers
            0x00, 0x00,    # Starting register (0)
            0x00, 0x01     # Number of registers (1)
        ])
        
        crc = calculate_crc(request)
        request.append(crc & 0xFF)
        request.append((crc >> 8) & 0xFF)
        
        # Send request
        ser.reset_input_buffer()
        ser.write(request)
        
        # Wait and read response
        time.sleep(0.2)
        response = ser.read(100)
        
        ser.close()
        
        return response
    except Exception as e:
        return None

def main():
    port = '/dev/ttyUSB0'
    slave_addresses = [1, 2, 3]  # Common addresses
    baudrates = [9600, 19200, 38400]
    parities = {
        'Even': serial.PARITY_EVEN,
        'None': serial.PARITY_NONE,
        'Odd': serial.PARITY_ODD
    }
    
    print("CFW300 VFD Diagnostic Tool")
    print("=" * 60)
    print(f"Testing port: {port}\n")
    
    # First, check if port exists and is accessible
    try:
        test_serial = serial.Serial(port, 9600, timeout=0.1)
        test_serial.close()
        print(f"✓ Port {port} is accessible\n")
    except Exception as e:
        print(f"✗ Cannot open port {port}: {e}")
        return
    
    print("Testing configurations...")
    print("-" * 60)
    
    success_count = 0
    
    for slave_addr in slave_addresses:
        for baudrate in baudrates:
            for parity_name, parity_val in parities.items():
                config = f"Addr:{slave_addr} {baudrate} 8{parity_name[0]}1"
                print(f"Testing {config}...", end=" ")
                
                response = test_modbus_connection(port, baudrate, parity_val, slave_addr)
                
                if response and len(response) >= 5:
                    # Check if it looks like a valid Modbus response
                    if response[0] == slave_addr and (response[1] == 0x03 or response[1] == 0x83):
                        print(f"✓ RESPONSE! ({len(response)} bytes)")
                        print(f"   Raw: {' '.join(f'{b:02X}' for b in response)}")
                        success_count += 1
                    else:
                        print(f"? Got {len(response)} bytes (unexpected format)")
                elif response and len(response) > 0:
                    print(f"? Partial response ({len(response)} bytes): {' '.join(f'{b:02X}' for b in response)}")
                else:
                    print("✗ No response")
    
    print("-" * 60)
    if success_count == 0:
        print("\n⚠ No successful connections found!")
        print("\nTroubleshooting steps:")
        print("1. Check RS485 wiring:")
        print("   - USB-RS485 A terminal → VFD A/+ terminal")
        print("   - USB-RS485 B terminal → VFD B/- terminal")
        print("2. Verify VFD is powered on")
        print("3. Check VFD communication settings in menu:")
        print("   - Serial communication should be enabled")
        print("   - Note the slave address (usually 1)")
        print("   - Note the baud rate (9600 is common)")
        print("4. Check if termination resistor is needed")
    else:
        print(f"\n✓ Found {success_count} working configuration(s)!")

if __name__ == "__main__":
    main()
