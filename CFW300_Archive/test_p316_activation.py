#!/usr/bin/env python3
"""
Send continuous Modbus frames and monitor if P316 ever changes from 0
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

def read_p316(ser):
    """Read P316 (Serial Interface Status)"""
    request = bytearray([0x01, 0x03, 0x01, 0x3C, 0x00, 0x01])  # Read register 316
    request += calculate_crc(request)
    
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    ser.write(request)
    time.sleep(0.15)
    
    response = ser.read(100)
    if len(response) >= 7 and response[0] == 0x01 and response[1] == 0x03:
        value = (response[3] << 8) | response[4]
        return value
    return None

def main():
    port = '/dev/ttyUSB0'
    
    print("="*70)
    print("TESTING IF VFD RS485 EVER ACTIVATES (P316)")
    print("="*70)
    print("\nSending Modbus read requests continuously...")
    print("Checking if P316 ever changes from 0 to 1 (Active)")
    print("\nPress Ctrl+C to stop\n")
    
    ser = serial.Serial(
        port=port,
        baudrate=19200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_EVEN,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.5
    )
    
    attempt = 0
    try:
        while True:
            attempt += 1
            
            # Try reading different parameters
            params_to_read = [1, 202, 220, 308, 310, 311, 312, 316, 680, 681]
            
            for param in params_to_read:
                # Build read request
                request = bytearray([0x01, 0x03, (param >> 8) & 0xFF, param & 0xFF, 0x00, 0x01])
                request += calculate_crc(request)
                
                ser.reset_input_buffer()
                ser.reset_output_buffer()
                ser.write(request)
                
                time.sleep(0.05)
                response = ser.read(100)
                
                if len(response) > 0:
                    print(f"Attempt {attempt}, P{param:03d}: Got {len(response)} bytes: {response.hex()}")
                
            # Check P316 status
            p316 = read_p316(ser)
            if p316 is not None and p316 != 0:
                print(f"\n*** P316 CHANGED TO {p316}! ***")
                if p316 == 1:
                    print("Serial interface is now ACTIVE!")
                elif p316 == 2:
                    print("Watchdog error detected")
                break
            
            if attempt % 10 == 0:
                print(f"Attempt {attempt}: P316 still 0 (or no response)")
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    finally:
        ser.close()

if __name__ == "__main__":
    main()
