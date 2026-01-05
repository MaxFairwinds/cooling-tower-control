#!/usr/bin/env python3
"""
Scan all baud rate and parity combinations to find what the VFD is actually using
"""
import serial
import time
import struct

def calculate_crc(data):
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return struct.pack('<H', crc)

def test_config(baudrate, parity, parity_name):
    """Test reading P001 with specific serial config"""
    try:
        ser = serial.Serial(
            port='/dev/ttyUSB0',
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=parity,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.2
        )
        
        # Read P001 (register 1)
        request = bytearray([0x01, 0x03, 0x00, 0x01, 0x00, 0x01])
        request += calculate_crc(request)
        
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        ser.write(request)
        time.sleep(0.1)
        
        response = ser.read(100)
        ser.close()
        
        if len(response) >= 7:
            # Valid Modbus response is: addr(1) + func(1) + len(1) + data(2) + crc(2) = 7 bytes
            if response[0] == 0x01 and response[1] == 0x03:
                return True, response
        elif len(response) > 0:
            return False, response
        
        return False, None
        
    except Exception as e:
        return False, None

def main():
    print("="*70)
    print("SCANNING ALL BAUD RATE AND PARITY COMBINATIONS")
    print("="*70)
    
    # Test combinations
    bauds = [9600, 19200, 38400, 57600, 76800]
    parities = [
        (serial.PARITY_NONE, 'N'),
        (serial.PARITY_EVEN, 'E'),
        (serial.PARITY_ODD, 'O')
    ]
    
    print(f"\n{'Baud':<8} {'Parity':<8} {'Result':<12} {'Response'}")
    print("-"*70)
    
    for baud in bauds:
        for parity, parity_name in parities:
            success, response = test_config(baud, parity, parity_name)
            
            if success:
                print(f"{baud:<8} {parity_name:<8} {'*** VALID ***':<12} {response.hex()}")
                print(f"\n*** FOUND WORKING CONFIGURATION: {baud} baud, 8{parity_name}1 ***\n")
                return
            elif response:
                print(f"{baud:<8} {parity_name:<8} {'Response':<12} {response.hex()}")
            else:
                print(f"{baud:<8} {parity_name:<8} {'No response':<12}")
    
    print("\nNo working configuration found")

if __name__ == "__main__":
    main()
