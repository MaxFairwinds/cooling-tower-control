#!/usr/bin/env python3
"""
Verify ALL VFD Modbus parameters are correct
"""
import serial
import time
import struct

def calculate_crc(data):
    """Calculate Modbus RTU CRC16"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return struct.pack('<H', crc)  # Little-endian

def read_parameter(ser, param_num, slave_addr=1):
    """Read a single VFD parameter using function 0x03"""
    # Build request
    request = bytearray([
        slave_addr,  # Slave address
        0x03,        # Function code: Read Holding Registers
        (param_num >> 8) & 0xFF,   # Register address high
        param_num & 0xFF,          # Register address low
        0x00,        # Number of registers high
        0x01         # Number of registers low (read 1)
    ])
    request += calculate_crc(request)
    
    # Clear buffers
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    
    # Send request
    ser.write(request)
    time.sleep(0.1)
    
    # Read response
    response = ser.read(ser.in_waiting or 100)
    
    if len(response) >= 7:
        # Check address and function
        if response[0] == slave_addr and response[1] == 0x03:
            # Extract value (2 bytes at positions 3-4)
            value = (response[3] << 8) | response[4]
            return value
    
    return None

def main():
    port = '/dev/ttyUSB0'
    
    print("="*70)
    print("COMPREHENSIVE VFD PARAMETER VERIFICATION")
    print("="*70)
    
    try:
        ser = serial.Serial(
            port=port,
            baudrate=19200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.5
        )
        
        print(f"\nConnected to {port}")
        print(f"Settings: 19200 baud, 8E1\n")
        
        # Parameters to check
        params = {
            'P202': (202, 'Control Type', {0: 'V/f', 3: 'Not Used'}),
            'P220': (220, 'LOC/REM Source', {6: 'Serial/USB'}),
            'P221': (221, 'Speed Ref LOCAL', {9: 'Serial/USB'}),
            'P222': (222, 'Speed Ref REMOTE', {9: 'Serial/USB'}),
            'P227': (227, 'Run/Stop REMOTE', {2: 'Serial/USB'}),
            'P228': (228, 'JOG REMOTE', {3: 'Serial/USB'}),
            'P308': (308, 'Serial Address', {}),
            'P310': (310, 'Baud Rate', {0: '9600', 1: '19200', 2: '38400'}),
            'P311': (311, 'Byte Config', {0: '8N1', 1: '8E1', 2: '8O1'}),
            'P312': (312, 'Serial Protocol', {0: 'Reserved', 1: 'Reserved', 2: 'Modbus RTU Slave', 3: 'BACnet', 5: 'Modbus RTU Master'}),
            'P313': (313, 'Comm Error Action', {0: 'Inactive', 1: 'Ramp Stop', 5: 'Cause Fault'}),
            'P314': (314, 'Serial Watchdog', {}),
            'P316': (316, 'Serial Status', {0: 'Inactive', 1: 'Active', 2: 'Watchdog Error'}),
        }
        
        print(f"{'Parameter':<12} {'Description':<20} {'Value':<8} {'Decoded'}")
        print("-"*70)
        
        for param_name, (param_num, description, decode_map) in params.items():
            value = read_parameter(ser, param_num)
            
            if value is not None:
                decoded = decode_map.get(value, f"({value})")
                status = "✓" if param_name == 'P316' or decoded != f"({value})" else "?"
                print(f"{param_name:<12} {description:<20} {value:<8} {decoded}")
            else:
                print(f"{param_name:<12} {description:<20} {'FAILED':<8} No response")
            
            time.sleep(0.2)
        
        ser.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
