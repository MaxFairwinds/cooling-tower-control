"""
Configuration for RaspCoolingTower system with 3 GALT G540 VFDs
"""

# VFD Configuration (GALT G540)
VFD_CONFIG = {
    'fan': {
        'device_id': 3,
        'description': 'Cooling Tower Fan Motor',
        'type': 'fan'
    },
    'pump_primary': {
        'device_id': 1,
        'description': 'Primary Pump Motor',
        'type': 'pump'
    },
    'pump_backup': {
        'device_id': 2,
        'description': 'Backup Pump Motor',
        'type': 'pump'
    }
}

# Serial Port Configuration (GALT G540 Actual Settings)
SERIAL_PORT = '/dev/ttyUSB0'  # USB-RS485 adapter (auto-detected)
SERIAL_BAUDRATE = 9600         # Found via scanner (P14.01=3)
SERIAL_PARITY = 'N'            # No parity (P14.02=0)
SERIAL_STOPBITS = 1
SERIAL_BYTESIZE = 8

# Control Parameters
CONTROL_PARAMS = {
    'target_pressure': 15.0,     # psi
    'pressure_tolerance': 2.0,   # psi
    'kp': 1.0,                   # Proportional gain
    'min_frequency': 20.0,       # Hz
    'max_frequency': 60.0,       # Hz
}

# Pump Failover Configuration
PUMP_FAILOVER = {
    'health_check_interval': 5.0,  # seconds
    'max_consecutive_errors': 3,
    'auto_failover_enabled': True
}

# Sensor Configuration (ADS1115)
SENSOR_CONFIG = {
    'i2c_address': 0x48,          # Default ADS1115 address
    'pressure_channel': 0,         # A0: Pressure sensor (0-100 psi, 0-5V)
    'temperature_channel': 1,      # A1: Temperature sensor
    'ads_gain': 1,                 # +/- 4.096V range
}

# Logging
LOG_FILE = 'cooling_tower.log'
LOG_LEVEL = 'INFO'
