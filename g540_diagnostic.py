#!/usr/bin/env python3
"""
GALT G540 VFD Modbus Diagnostic Tool
Tests communication with GALT G500 series VFD via RS485 Modbus RTU

Based on GALT G500 manual specifications:
- Default baud: 19200 (P14.01=4)
- Default parity: Even (E,8,1) (P14.02=1)
- Default slave address: 1 (P14.00=1)
- Function codes: 03H (read), 06H (write), 10H (multi-write)
"""

import serial
import struct
import time
import sys

# ==================== CONFIGURATION ====================
PORT = '/dev/ttyUSB0'           # USB-RS485 adapter
BAUD_RATE = 9600                # Found via scanner: 9600 (P14.01=3)
PARITY = serial.PARITY_NONE     # Found via scanner: None (P14.02=0)
SLAVE_ADDR = 3                  # Fan VFD address (P14.00=3)
TIMEOUT = 1.0                   # 1 second timeout

# ==================== REGISTER MAP ====================
# Control commands (write to 0x2000)
CMD_FORWARD = 0x0001
CMD_REVERSE = 0x0002
CMD_STOP = 0x0005
CMD_COAST_STOP = 0x0006
CMD_FAULT_RESET = 0x0007

# Control/monitoring addresses
REG_CONTROL_CMD = 0x2000        # Control command
REG_FREQ_SET = 0x2001           # Frequency setting (0.01 Hz units)
REG_STATE_1 = 0x2100            # State word 1
REG_STATE_2 = 0x2101            # State word 2
REG_FAULT_CODE = 0x2102         # Fault code
REG_IDENT = 0x2103              # Identification code (should be 0x01A1)

# Monitoring addresses
REG_RUN_FREQ = 0x3000           # Running frequency (0.01 Hz)
REG_SET_FREQ = 0x3001           # Set frequency (0.01 Hz)
REG_BUS_VOLTAGE = 0x3002        # Bus voltage (0.1 V)
REG_OUTPUT_VOLTAGE = 0x3003     # Output voltage (1 V)
REG_OUTPUT_CURRENT = 0x3004     # Output current (0.1 A)
REG_ROTATING_SPEED = 0x3005     # Rotating speed (RPM)
REG_OUTPUT_POWER = 0x3006       # Output power (0.1 %)
REG_OUTPUT_TORQUE = 0x3007      # Output torque (0.1 %)

# Parameter addresses (function codes)
PARAM_CMD_CHANNEL = 0x0001      # P00.01: Running command channel
PARAM_COMM_CHANNEL = 0x0002     # P00.02: Communication running command channel
PARAM_COMM_ADDR = 0x1400        # P14.00: Local communication address
PARAM_COMM_BAUD = 0x1401        # P14.01: Communication baud rate
PARAM_COMM_PARITY = 0x1402      # P14.02: Data bit check setting

# State word 1 values
STATE_FORWARD = 0x0001
STATE_REVERSE = 0x0002
STATE_STOPPED = 0x0003
STATE_FAULT = 0x0004
STATE_POFF = 0x0005
STATE_PRE_EXCITED = 0x0006

# State word 2 bit definitions
STATE2_READY = 0x0001           # Bit 0: Ready to run
STATE2_OVERLOAD = 0x0010        # Bit 4: Overload alarm
STATE2_CTRL_KEYPAD = 0x0000     # Bits 6-5: Keypad control
STATE2_CTRL_TERMINAL = 0x0020   # Bits 6-5: Terminal control
STATE2_CTRL_COMM = 0x0040       # Bits 6-5: Communication control

# ==================== MODBUS FUNCTIONS ====================

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

def read_registers(ser, slave_addr, register, count=1):
    """Read holding registers (function code 0x03)"""
    # Build request: [addr][0x03][reg_hi][reg_lo][count_hi][count_lo][crc]
    request = bytes([
        slave_addr,
        0x03,
        (register >> 8) & 0xFF,
        register & 0xFF,
        (count >> 8) & 0xFF,
        count & 0xFF
    ])
    request += crc16(request)
    
    # Send request
    ser.write(request)
    print(f"TX: {request.hex()}")
    
    # Receive response
    time.sleep(0.1)
    response = ser.read(256)
    print(f"RX: {response.hex()}")
    
    if len(response) < 5:
        print(f"ERROR: Response too short ({len(response)} bytes)")
        return None
    
    # Verify CRC
    if response[-2:] != crc16(response[:-2]):
        print(f"ERROR: CRC mismatch")
        return None
    
    # Check for exception
    if response[1] & 0x80:
        exception_code = response[2]
        print(f"ERROR: Exception code {exception_code:02X}")
        return None
    
    # Extract data
    byte_count = response[2]
    data = response[3:3+byte_count]
    
    # Convert to 16-bit values
    values = []
    for i in range(0, len(data), 2):
        values.append((data[i] << 8) | data[i+1])
    
    return values

def write_register(ser, slave_addr, register, value):
    """Write single register (function code 0x06)"""
    # Build request: [addr][0x06][reg_hi][reg_lo][val_hi][val_lo][crc]
    request = bytes([
        slave_addr,
        0x06,
        (register >> 8) & 0xFF,
        register & 0xFF,
        (value >> 8) & 0xFF,
        value & 0xFF
    ])
    request += crc16(request)
    
    # Send request
    ser.write(request)
    print(f"TX: {request.hex()}")
    
    # Receive response
    time.sleep(0.1)
    response = ser.read(256)
    print(f"RX: {response.hex()}")
    
    if len(response) < 5:
        print(f"ERROR: Response too short ({len(response)} bytes)")
        return False
    
    # Verify CRC
    if response[-2:] != crc16(response[:-2]):
        print(f"ERROR: CRC mismatch")
        return False
    
    # Check for exception
    if response[1] & 0x80:
        exception_code = response[2]
        print(f"ERROR: Exception code {exception_code:02X}")
        return False
    
    return True

# ==================== DIAGNOSTIC FUNCTIONS ====================

def decode_state_word_1(state):
    """Decode state word 1"""
    states = {
        0x0001: "Forward running",
        0x0002: "Reverse running",
        0x0003: "Stopped",
        0x0004: "Fault",
        0x0005: "Power off",
        0x0006: "Pre-excited"
    }
    return states.get(state, f"Unknown (0x{state:04X})")

def decode_state_word_2(state):
    """Decode state word 2 bits"""
    info = []
    
    # Bit 0: Ready
    if state & 0x0001:
        info.append("Ready to run")
    else:
        info.append("Not ready")
    
    # Bits 2-1: Motor number
    motor = (state >> 1) & 0x03
    info.append(f"Motor {motor + 1}")
    
    # Bit 3: Motor type
    if state & 0x0008:
        info.append("Synchronous motor")
    else:
        info.append("Asynchronous motor")
    
    # Bit 4: Overload
    if state & 0x0010:
        info.append("OVERLOAD ALARM")
    
    # Bits 6-5: Control mode
    ctrl = (state >> 5) & 0x03
    ctrl_modes = ["Keypad", "Terminal", "Communication"]
    if ctrl < 3:
        info.append(f"{ctrl_modes[ctrl]} control")
    
    # Bit 8: Control type
    if state & 0x0100:
        info.append("Torque control")
    else:
        info.append("Speed control")
    
    return " | ".join(info)

def test_basic_communication(ser):
    """Test basic Modbus communication"""
    print("\n" + "="*70)
    print("BASIC COMMUNICATION TEST")
    print("="*70)
    
    # Test 1: Read identification code
    print("\n[TEST 1] Reading VFD identification code (should be 0x01A1 for G500)...")
    result = read_registers(ser, SLAVE_ADDR, REG_IDENT, 1)
    if result:
        ident = result[0]
        print(f"✓ Identification: 0x{ident:04X}", end="")
        if ident == 0x01A1:
            print(" (CONFIRMED: GALT G500 series)")
        else:
            print(" (WARNING: Unexpected value)")
        return True
    else:
        print("✗ FAILED: No response from VFD")
        return False

def read_vfd_config(ser):
    """Read VFD configuration parameters"""
    print("\n" + "="*70)
    print("VFD CONFIGURATION")
    print("="*70)
    
    params = [
        (PARAM_CMD_CHANNEL, "P00.01: Running command channel", {0: "Keypad", 1: "Terminal", 2: "Communication"}),
        (PARAM_COMM_CHANNEL, "P00.02: Communication running command channel", {0: "Modbus/Modbus TCP", 1: "PROFIBUS/CANopen/DeviceNet/G500XLT"}),
        (PARAM_COMM_ADDR, "P14.00: Communication address", None),
        (PARAM_COMM_BAUD, "P14.01: Baud rate", {0: "1200", 1: "2400", 2: "4800", 3: "9600", 4: "19200", 5: "38400", 6: "57600", 7: "115200"}),
        (PARAM_COMM_PARITY, "P14.02: Parity", {0: "N,8,1", 1: "E,8,1", 2: "O,8,1", 3: "N,8,2", 4: "E,8,2", 5: "O,8,2"}),
    ]
    
    for addr, name, mapping in params:
        result = read_registers(ser, SLAVE_ADDR, addr, 1)
        if result:
            value = result[0]
            if mapping:
                decoded = mapping.get(value, f"Unknown ({value})")
                print(f"{name}: {decoded}")
            else:
                print(f"{name}: {value}")
        else:
            print(f"{name}: READ FAILED")

def read_vfd_status(ser):
    """Read VFD operational status"""
    print("\n" + "="*70)
    print("VFD STATUS")
    print("="*70)
    
    # State word 1
    result = read_registers(ser, SLAVE_ADDR, REG_STATE_1, 1)
    if result:
        state1 = result[0]
        print(f"State Word 1: {decode_state_word_1(state1)}")
    else:
        print("State Word 1: READ FAILED")
    
    # State word 2
    result = read_registers(ser, SLAVE_ADDR, REG_STATE_2, 1)
    if result:
        state2 = result[0]
        print(f"State Word 2: {decode_state_word_2(state2)}")
    else:
        print("State Word 2: READ FAILED")
    
    # Fault code
    result = read_registers(ser, SLAVE_ADDR, REG_FAULT_CODE, 1)
    if result:
        fault = result[0]
        if fault == 0:
            print(f"Fault Code: None (0x0000)")
        else:
            print(f"Fault Code: 0x{fault:04X}")
    else:
        print("Fault Code: READ FAILED")

def read_vfd_measurements(ser):
    """Read VFD measurements"""
    print("\n" + "="*70)
    print("VFD MEASUREMENTS")
    print("="*70)
    
    measurements = [
        (REG_RUN_FREQ, "Running Frequency", 0.01, "Hz"),
        (REG_SET_FREQ, "Set Frequency", 0.01, "Hz"),
        (REG_BUS_VOLTAGE, "Bus Voltage", 0.1, "V"),
        (REG_OUTPUT_VOLTAGE, "Output Voltage", 1.0, "V"),
        (REG_OUTPUT_CURRENT, "Output Current", 0.1, "A"),
        (REG_ROTATING_SPEED, "Rotating Speed", 1.0, "RPM"),
        (REG_OUTPUT_POWER, "Output Power", 0.1, "%"),
        (REG_OUTPUT_TORQUE, "Output Torque", 0.1, "%"),
    ]
    
    for addr, name, scale, unit in measurements:
        result = read_registers(ser, SLAVE_ADDR, addr, 1)
        if result:
            raw = result[0]
            # Handle signed values for torque and power
            if raw > 32767:
                raw = raw - 65536
            value = raw * scale
            print(f"{name:20s}: {value:8.2f} {unit}")
        else:
            print(f"{name:20s}: READ FAILED")

def test_control_sequence(ser):
    """Test VFD control via Modbus (REQUIRES P00.01=2, P00.02=0)"""
    print("\n" + "="*70)
    print("CONTROL SEQUENCE TEST")
    print("="*70)
    print("NOTE: This test requires:")
    print("  P00.01 = 2 (Communication control)")
    print("  P00.02 = 0 (Modbus channel)")
    print()
    
    input("Press ENTER to continue or Ctrl+C to skip...")
    
    # Test 1: Set frequency to 10.00 Hz (send 1000 = 0x03E8)
    print("\n[TEST 1] Setting frequency to 10.00 Hz...")
    if write_register(ser, SLAVE_ADDR, REG_FREQ_SET, 1000):
        print("✓ Frequency set command sent")
        time.sleep(0.5)
        
        # Verify
        result = read_registers(ser, SLAVE_ADDR, REG_SET_FREQ, 1)
        if result:
            freq = result[0] * 0.01
            print(f"✓ Verified: Set frequency = {freq:.2f} Hz")
    else:
        print("✗ FAILED to set frequency")
    
    # Test 2: Send forward run command
    print("\n[TEST 2] Sending FORWARD RUN command...")
    if write_register(ser, SLAVE_ADDR, REG_CONTROL_CMD, CMD_FORWARD):
        print("✓ Forward run command sent")
        print("⚠ WARNING: Motor should be running now!")
        time.sleep(2)
        
        # Check status
        result = read_registers(ser, SLAVE_ADDR, REG_STATE_1, 1)
        if result:
            state = result[0]
            print(f"✓ State: {decode_state_word_1(state)}")
    else:
        print("✗ FAILED to send run command")
    
    # Test 3: Stop motor
    print("\n[TEST 3] Sending STOP command...")
    if write_register(ser, SLAVE_ADDR, REG_CONTROL_CMD, CMD_STOP):
        print("✓ Stop command sent")
        time.sleep(1)
        
        # Check status
        result = read_registers(ser, SLAVE_ADDR, REG_STATE_1, 1)
        if result:
            state = result[0]
            print(f"✓ State: {decode_state_word_1(state)}")
    else:
        print("✗ FAILED to send stop command")

# ==================== MAIN ====================

def main():
    print("="*70)
    print("GALT G540 VFD MODBUS DIAGNOSTIC")
    print("="*70)
    print(f"Port: {PORT}")
    print(f"Baud: {BAUD_RATE}")
    print(f"Parity: Even (E,8,1)")
    print(f"Slave Address: {SLAVE_ADDR}")
    print()
    
    try:
        # Open serial port
        ser = serial.Serial(
            port=PORT,
            baudrate=BAUD_RATE,
            bytesize=serial.EIGHTBITS,
            parity=PARITY,
            stopbits=serial.STOPBITS_ONE,
            timeout=TIMEOUT
        )
        
        print(f"✓ Serial port opened: {ser.name}")
        
        # Run diagnostics
        if not test_basic_communication(ser):
            print("\n✗ CRITICAL: VFD not responding. Check:")
            print("  1. RS485 wiring (A-A, B-B, GND-GND)")
            print("  2. VFD power")
            print("  3. Slave address (P14.00)")
            print("  4. Baud rate (P14.01)")
            print("  5. Parity setting (P14.02)")
            sys.exit(1)
        
        read_vfd_config(ser)
        read_vfd_status(ser)
        read_vfd_measurements(ser)
        
        # Optional control test
        try:
            test_control_sequence(ser)
        except KeyboardInterrupt:
            print("\nControl test skipped by user")
        
        print("\n" + "="*70)
        print("DIAGNOSTIC COMPLETE")
        print("="*70)
        
        ser.close()
        
    except serial.SerialException as e:
        print(f"\n✗ ERROR: {e}")
        print(f"Check that {PORT} exists and is not in use")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nDiagnostic interrupted by user")
        sys.exit(1)

if __name__ == "__main__":
    main()
