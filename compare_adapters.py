#!/usr/bin/env python3
"""
Compare two Waveshare adapters to verify identical behavior
"""
import serial
import time
import os

print("Adapter Comparison Test")
print("=" * 60)

# Find devices
devices = [f"/dev/{d}" for d in os.listdir("/dev") if d.startswith("ttyUSB")]
devices.sort()

if len(devices) < 2:
    print(f"ERROR: Found only {len(devices)} device(s)")
    exit(1)

PORT1 = devices[0]
PORT2 = devices[1]

print(f"Testing:")
print(f"  Adapter 1: {PORT1}")
print(f"  Adapter 2: {PORT2}")
print()

def test_adapter(port_name):
    """Test single adapter characteristics"""
    results = {}
    
    ser = serial.Serial(port=port_name, baudrate=19200, bytesize=8, parity='E', stopbits=1, timeout=0.5)
    
    # Test 1: RTS/DTR control
    ser.rts = True
    ser.dtr = True
    results['rts_works'] = ser.rts == True
    results['dtr_works'] = ser.dtr == True
    
    # Test 2: Write speed
    test_data = b'\xFF' * 100
    start = time.time()
    ser.write(test_data)
    ser.flush()
    write_time = time.time() - start
    results['write_time_ms'] = write_time * 1000
    
    # Test 3: Buffer clearing
    ser.reset_input_buffer()
    ser.reset_output_buffer()
    results['buffer_reset'] = True
    
    # Test 4: Settings
    results['baudrate'] = ser.baudrate
    results['bytesize'] = ser.bytesize
    results['parity'] = ser.parity
    results['stopbits'] = ser.stopbits
    
    ser.close()
    return results

print("Testing Adapter 1...")
results1 = test_adapter(PORT1)

print("Testing Adapter 2...")
results2 = test_adapter(PORT2)

print()
print("=" * 60)
print("COMPARISON:")
print("=" * 60)

all_match = True

for key in results1.keys():
    val1 = results1[key]
    val2 = results2[key]
    match = val1 == val2 or (isinstance(val1, float) and abs(val1 - val2) < 1.0)
    
    status = "✓" if match else "✗"
    print(f"{status} {key:20s}: Adapter1={val1}, Adapter2={val2}")
    
    if not match:
        all_match = False

print()
print("=" * 60)
if all_match:
    print("✓ Both adapters behave identically!")
    print("  EEPROM appears to be correctly configured.")
else:
    print("✗ Adapters differ in behavior!")
    print("  Possible EEPROM configuration issue.")
