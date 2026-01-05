#!/usr/bin/env python3
"""
GALT G540 VFD Scanner
Scans for VFD by trying different baud rates, parity, and slave addresses
"""

import serial
import struct
import time
import sys

PORT = '/dev/ttyUSB0'
TIMEOUT = 0.5  # Shorter timeout for scanning

# Register to test - Identification should return 0x01A1 for G500
TEST_REGISTER = 0x2103

def crc16(data):
    """Calculate Modbus RTU CRC-16"""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return struct.pack('<H', crc)

def test_connection(ser, slave_addr, register=TEST_REGISTER):
    """Try to read a register and return True if successful"""
    try:
        # Build request to read 1 register
        request = bytes([
            slave_addr,
            0x03,
            (register >> 8) & 0xFF,
            register & 0xFF,
            0x00,
            0x01
        ])
        request += crc16(request)
        
        # Clear buffers
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        # Send request
        ser.write(request)
        time.sleep(0.05)
        
        # Read response
        response = ser.read(256)
        
        # Check minimum length
        if len(response) < 7:
            return None
        
        # Verify CRC
        if response[-2:] != crc16(response[:-2]):
            return None
        
        # Check for exception
        if response[1] & 0x80:
            return None
        
        # Extract value
        if len(response) >= 7:
            value = (response[3] << 8) | response[4]
            return value
        
        return None
        
    except Exception:
        return None

def main():
    print("="*70)
    print("GALT G540 VFD SCANNER")
    print("="*70)
    print(f"Port: {PORT}")
    print("Scanning for VFD with different settings...\n")
    
    # Baud rates to try (most common first)
    baud_rates = [
        19200,   # G500 default
        9600,    # Very common
        38400,
        115200,
        57600,
        4800,
        2400,
        1200
    ]
    
    # Parity settings to try
    parity_settings = [
        (serial.PARITY_EVEN, "Even", "E,8,1"),    # G500 default
        (serial.PARITY_NONE, "None", "N,8,1"),
        (serial.PARITY_ODD, "Odd", "O,8,1"),
        (serial.PARITY_NONE, "None", "N,8,2"),    # 2 stop bits
    ]
    
    # Slave addresses to try (most common first)
    slave_addresses = list(range(1, 11))  # 1-10
    
    total_tests = len(baud_rates) * len(parity_settings) * len(slave_addresses)
    test_count = 0
    
    try:
        for baud in baud_rates:
            for parity_val, parity_name, parity_desc in parity_settings:
                
                # Determine stop bits
                stopbits = serial.STOPBITS_TWO if "8,2" in parity_desc else serial.STOPBITS_ONE
                
                # Open port with these settings
                try:
                    ser = serial.Serial(
                        port=PORT,
                        baudrate=baud,
                        bytesize=serial.EIGHTBITS,
                        parity=parity_val,
                        stopbits=stopbits,
                        timeout=TIMEOUT
                    )
                except serial.SerialException as e:
                    print(f"ERROR: Cannot open {PORT}: {e}")
                    sys.exit(1)
                
                # Try each slave address
                for slave in slave_addresses:
                    test_count += 1
                    
                    # Show progress every 20 tests
                    if test_count % 20 == 0:
                        progress = (test_count / total_tests) * 100
                        print(f"Progress: {test_count}/{total_tests} ({progress:.0f}%)...")
                    
                    # Test this configuration
                    result = test_connection(ser, slave)
                    
                    if result is not None:
                        print("\n" + "="*70)
                        print("✓ VFD FOUND!")
                        print("="*70)
                        print(f"Baud Rate:     {baud}")
                        print(f"Parity:        {parity_desc}")
                        print(f"Slave Address: {slave}")
                        print(f"Identification: 0x{result:04X}", end="")
                        
                        if result == 0x01A1:
                            print(" (CONFIRMED: GALT G500 series)")
                        else:
                            print(" (Unknown device)")
                        
                        print("\nTo use these settings in g540_diagnostic.py:")
                        print(f"  BAUD_RATE = {baud}")
                        
                        if parity_val == serial.PARITY_EVEN:
                            print(f"  PARITY = serial.PARITY_EVEN")
                        elif parity_val == serial.PARITY_ODD:
                            print(f"  PARITY = serial.PARITY_ODD")
                        else:
                            print(f"  PARITY = serial.PARITY_NONE")
                        
                        print(f"  SLAVE_ADDR = {slave}")
                        
                        # Try to read more info
                        print("\nAttempting to read additional parameters...")
                        
                        # Try to read state word 1 (0x2100)
                        state1 = test_connection(ser, slave, 0x2100)
                        if state1 is not None:
                            states = {
                                0x0001: "Forward running",
                                0x0002: "Reverse running", 
                                0x0003: "Stopped",
                                0x0004: "Fault",
                                0x0005: "Power off",
                                0x0006: "Pre-excited"
                            }
                            state_str = states.get(state1, f"Unknown (0x{state1:04X})")
                            print(f"  VFD State: {state_str}")
                        
                        # Try to read running frequency (0x3000)
                        freq = test_connection(ser, slave, 0x3000)
                        if freq is not None:
                            freq_hz = freq * 0.01
                            print(f"  Running Frequency: {freq_hz:.2f} Hz")
                        
                        # Try to read bus voltage (0x3002)
                        bus_v = test_connection(ser, slave, 0x3002)
                        if bus_v is not None:
                            voltage = bus_v * 0.1
                            print(f"  Bus Voltage: {voltage:.1f} V")
                        
                        ser.close()
                        print("\n" + "="*70)
                        return
                
                ser.close()
        
        # If we get here, nothing was found
        print("\n" + "="*70)
        print("✗ NO VFD FOUND")
        print("="*70)
        print("Tried:")
        print(f"  Baud rates: {', '.join(map(str, baud_rates))}")
        print(f"  Parity: Even, None, Odd")
        print(f"  Slave addresses: 1-10")
        print("\nTroubleshooting:")
        print("  1. Check RS485 wiring (A-A, B-B, GND-GND)")
        print("  2. Verify VFD power is ON")
        print("  3. Try swapping A and B lines (reverse polarity)")
        print("  4. Check if slave address is > 10 (uncommon)")
        print("  5. Verify RS485 adapter is recognized")
        print(f"     Run: ls -la {PORT}")
        
    except KeyboardInterrupt:
        print("\n\nScan interrupted by user")
        if 'ser' in locals():
            ser.close()
    except Exception as e:
        print(f"\nERROR: {e}")
        if 'ser' in locals():
            ser.close()

if __name__ == "__main__":
    main()
