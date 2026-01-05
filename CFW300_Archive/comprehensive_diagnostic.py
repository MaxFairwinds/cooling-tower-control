#!/usr/bin/env python3
"""
Comprehensive RS485/Modbus diagnostic script
Re-verifies all critical data points and settings
"""

import serial
import time
import struct

PORT = '/dev/ttyUSB0'
BAUD = 19200
VFD_ADDRESS = 1

def crc16_modbus(data):
    """Calculate Modbus CRC16"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return struct.pack('<H', crc)

def modbus_read_holding(address, register, count=1):
    """Build Modbus Read Holding Registers (0x03) request"""
    msg = bytes([
        address,           # Slave address
        0x03,             # Function code
        register >> 8,    # Register high byte
        register & 0xFF,  # Register low byte
        count >> 8,       # Count high byte
        count & 0xFF      # Count low byte
    ])
    msg += crc16_modbus(msg)
    return msg

def test_parameter(ser, param_num, param_name, expected_value=None):
    """Test reading a specific VFD parameter"""
    print(f"\n{'='*60}")
    print(f"Testing {param_name} (P{param_num:03d})")
    print(f"{'='*60}")
    
    # Calculate register address (P001 = register 1, P202 = register 202, etc.)
    # Per WEG Modbus RTU manual page 18: "parameter number corresponds to the register address"
    register = param_num
    
    # Build request
    request = modbus_read_holding(VFD_ADDRESS, register, 1)
    print(f"TX ({len(request)} bytes): {' '.join(f'{b:02X}' for b in request)}")
    
    # Clear buffers
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    
    # Send request
    tx_start = time.time()
    ser.write(request)
    ser.flush()
    tx_duration = time.time() - tx_start
    
    # Wait for response
    time.sleep(0.1)  # 100ms response window
    
    rx_start = time.time()
    response = ser.read(100)  # Read up to 100 bytes
    rx_duration = time.time() - rx_start
    
    print(f"TX Duration: {tx_duration*1000:.2f}ms")
    print(f"RX Duration: {rx_duration*1000:.2f}ms")
    print(f"RX ({len(response)} bytes): {' '.join(f'{b:02X}' for b in response) if response else 'NONE'}")
    
    # Parse response if valid length
    if len(response) == 7:  # Valid Modbus response for 1 register
        addr, func, byte_count, val_high, val_low, crc_low, crc_high = response
        value = (val_high << 8) | val_low
        
        # Verify CRC
        expected_crc = crc16_modbus(response[:-2])
        actual_crc = bytes([crc_low, crc_high])
        crc_valid = expected_crc == actual_crc
        
        print(f"\n✓ Valid Response:")
        print(f"  Address: {addr} (expected {VFD_ADDRESS})")
        print(f"  Function: 0x{func:02X} (expected 0x03)")
        print(f"  Byte Count: {byte_count} (expected 2)")
        print(f"  Value: {value}")
        print(f"  CRC: {'VALID' if crc_valid else 'INVALID'}")
        
        if expected_value is not None:
            if value == expected_value:
                print(f"  ✓ Matches expected value: {expected_value}")
            else:
                print(f"  ✗ MISMATCH! Expected: {expected_value}, Got: {value}")
        
        return value
    elif len(response) > 0:
        print(f"✗ Invalid response length (expected 7 bytes)")
        # Check if it's an error response
        if len(response) >= 3:
            addr, func, error_code = response[0], response[1], response[2]
            if func & 0x80:  # Error bit set
                print(f"  Modbus Error Response:")
                print(f"    Address: {addr}")
                print(f"    Function: 0x{func:02X}")
                print(f"    Error Code: 0x{error_code:02X}")
        return None
    else:
        print(f"✗ No response received")
        return None

def main():
    print("="*70)
    print("COMPREHENSIVE RS485/MODBUS DIAGNOSTIC")
    print("="*70)
    print(f"Port: {PORT}")
    print(f"Baud: {BAUD}")
    print(f"Parity: Even")
    print(f"VFD Address: {VFD_ADDRESS}")
    print()
    
    try:
        # Open serial port
        ser = serial.Serial(
            port=PORT,
            baudrate=BAUD,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            timeout=0.5,
            write_timeout=1.0
        )
        
        print(f"✓ Port opened successfully")
        print(f"  Settings: {ser}")
        print()
        
        time.sleep(0.5)  # Initial settling time
        
        # Test critical parameters in order
        results = {}
        
        # P001 - Basic test
        results['P001'] = test_parameter(ser, 1, "P001 (First Parameter)", None)
        time.sleep(0.2)
        
        # P202 - CRITICAL: Must be 3 for serial control
        results['P202'] = test_parameter(ser, 202, "P202 (Source Selection)", 3)
        time.sleep(0.2)
        
        # P220 - Remote source
        results['P220'] = test_parameter(ser, 220, "P220 (Remote Source)", 6)
        time.sleep(0.2)
        
        # P308 - Modbus address
        results['P308'] = test_parameter(ser, 308, "P308 (Modbus Address)", 1)
        time.sleep(0.2)
        
        # P310 - Baud rate
        results['P310'] = test_parameter(ser, 310, "P310 (Baud Rate)", 1)
        time.sleep(0.2)
        
        # P311 - Serial format
        results['P311'] = test_parameter(ser, 311, "P311 (Serial Format)", 1)
        time.sleep(0.2)
        
        # P312 - Protocol
        results['P312'] = test_parameter(ser, 312, "P312 (Protocol)", 2)
        time.sleep(0.2)
        
        # P316 - Communication counter
        results['P316'] = test_parameter(ser, 316, "P316 (Comm Counter)", 0)
        time.sleep(0.2)
        
        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)
        
        success_count = sum(1 for v in results.values() if v is not None)
        print(f"\nSuccessful reads: {success_count}/{len(results)}")
        
        print("\nParameter Values:")
        for param, value in results.items():
            status = "✓" if value is not None else "✗"
            print(f"  {status} {param}: {value if value is not None else 'NO RESPONSE'}")
        
        # Check critical parameters
        print("\nCritical Parameter Check:")
        critical_checks = [
            ('P202', 3, 'Serial control enabled'),
            ('P308', 1, 'Modbus address correct'),
            ('P310', 1, '19200 baud rate'),
            ('P311', 1, '8E1 format'),
            ('P312', 2, 'Modbus RTU protocol'),
        ]
        
        all_critical_ok = True
        for param, expected, description in critical_checks:
            actual = results.get(param)
            if actual == expected:
                print(f"  ✓ {param} = {expected}: {description}")
            elif actual is None:
                print(f"  ✗ {param} = NO RESPONSE (expected {expected}): {description}")
                all_critical_ok = False
            else:
                print(f"  ✗ {param} = {actual} (expected {expected}): {description}")
                all_critical_ok = False
        
        if all_critical_ok:
            print("\n✓ All critical parameters verified correct!")
        else:
            print("\n✗ Some critical parameters are incorrect or unreadable")
        
        # Check P316 counter
        if results.get('P316') == 0:
            print("\n⚠ WARNING: P316 = 0 indicates VFD has not detected ANY valid communication")
        elif results.get('P316') is not None:
            print(f"\n✓ P316 = {results['P316']}: VFD has detected valid frames")
        
        ser.close()
        
    except serial.SerialException as e:
        print(f"\n✗ Serial error: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
