"""
Configuration for CFW300 Test Environment

WEG CFW300 VFD Testing on Raspberry Pi
Device IDs: 101, 102, 103 (clearly separated from production G540s)
"""

# VFD Configuration - CFW300 Test Units
VFD_CONFIG = {
    'test_vfd_1': {
        'device_id': 100,
        'description': 'CFW300 Test Unit #1',
        'type': 'test'
    },
    'test_vfd_2': {
        'device_id': 102,
        'description': 'CFW300 Test Unit #2',
        'type': 'test'
    },
    'test_vfd_3': {
        'device_id': 103,
        'description': 'CFW300 Test Unit #3',
        'type': 'test'
    }
}

# Serial Port Configuration
SERIAL_PORT = '/dev/ttyS0'
SERIAL_BAUDRATE = 9600  # Match CFW300 P300 setting
SERIAL_PARITY = 'N'      # Match CFW300 P302 setting
SERIAL_TIMEOUT = 1.0     # seconds

# CFW300 Modbus Register Map
# Based on WEG CFW300 documentation
CFW300_REGISTERS = {
    # Control and Status
    'CONTROL_WORD': 682,      # P682 - Serial Control Word (write)
    'STATUS_WORD': 683,       # P683 - Status Word (read)
    'SPEED_REFERENCE': 681,   # P681 - Speed Reference (write, scaled 0-8191)
    'ACTUAL_SPEED': 681,      # P681 - Also reads actual speed
    'FAULT_CODE': 48,         # P048 - Last fault code
    
    # Configuration Parameters (for reference)
    'CMD_SOURCE': 220,        # P220 - Command source (set to Serial)
    'SPEED_REF_SOURCE': 221,  # P221 - Speed reference source (set to Serial)
    'RS485_ADDRESS': 308,     # P308 - RS-485 address (1-247)
    'RS485_BAUDRATE': 310,    # P310 - Baud rate (0=9600, 1=19200)
    'RS485_PARITY': 311,      # P311 - Parity (0=None, 1=Odd, 2=Even)
    'COMM_TIMEOUT': 313,      # P313 - Communication timeout behavior
}

# CFW300 Control Word Bits (P682)
# Bit definitions for control word
CONTROL_BITS = {
    'RUN_FORWARD': 0x0001,     # Bit 0: Run forward
    'RUN_REVERSE': 0x0002,     # Bit 1: Run reverse  
    'JOG': 0x0004,             # Bit 2: Jog
    'ENABLE': 0x0200,          # Bit 9: General enable
    'FAULT_RESET': 0x0080,     # Bit 7: Fault reset
}

# Speed Scaling
# CFW300 uses 13-bit resolution: 0-8191 maps to 0-rated frequency
SPEED_SCALE_MAX = 8191  # 13-bit max value (0x1FFF)
RATED_FREQUENCY = 60.0  # Hz - match P403 setting on CFW300

# Test Parameters
TEST_PARAMS = {
    'test_frequency_min': 10.0,   # Hz
    'test_frequency_max': 50.0,   # Hz
    'ramp_step': 5.0,             # Hz per step
    'step_duration': 2.0,         # seconds
    'retry_count': 3,
    'retry_delay': 0.5,           # seconds
}

# Logging
LOG_FILE = 'test_cfw300.log'
LOG_LEVEL = 'DEBUG'  # More verbose for testing
