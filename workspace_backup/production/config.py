"""
Configuration for RaspCoolingTower system with 3 VFDs
"""

# VFD Configuration
VFD_CONFIG = {
    'fan': {
        'device_id': 1,
        'description': 'Cooling Tower Fan Motor',
        'type': 'fan'
    },
    'pump_primary': {
        'device_id': 2,
        'description': 'Primary Pump Motor',
        'type': 'pump'
    },
    'pump_backup': {
        'device_id': 3,
        'description': 'Backup Pump Motor',
        'type': 'pump'
    }
}

# Serial Port Configuration
SERIAL_PORT = '/dev/ttyS0'
SERIAL_BAUDRATE = 9600

# Control Parameters
CONTROL_PARAMS = {
    'target_pressure': 50.0,  # psi
    'pressure_tolerance': 2.0,  # psi
    'kp': 1.0,  # Proportional gain
    'min_frequency': 20.0,  # Hz
    'max_frequency': 60.0,  # Hz
}

# Pump Failover Configuration
PUMP_FAILOVER = {
    'health_check_interval': 5.0,  # seconds
    'max_consecutive_errors': 3,
    'auto_failover_enabled': True
}

# Logging
LOG_FILE = 'system.log'
LOG_LEVEL = 'INFO'
