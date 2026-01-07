#!/usr/bin/env python3
"""
Long-term data logger for cooling tower sensors
Logs all sensor data (pressure, water temp, air temp) to CSV file
"""

import time
import logging
from datetime import datetime
from sensor_manager import SensorManager
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Data file location
LOG_DIR = '/var/log/cooling-tower'
LOG_FILE = os.path.join(LOG_DIR, 'sensor_data.csv')

# Create log directory if it doesn't exist
os.makedirs(LOG_DIR, exist_ok=True)

# Initialize sensor manager
try:
    sensors = SensorManager(i2c_address=0x48, gain=1)
    logger.info("Sensor manager initialized")
except Exception as e:
    logger.error(f"Failed to initialize sensors: {e}")
    exit(1)

# Check if CSV file exists, create with header if not
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w') as f:
        f.write("timestamp,pressure_psi,pressure_voltage,water_temp_f,water_voltage,air_temp_f,air_voltage,air_resistance_ohms\n")
    logger.info(f"Created new log file: {LOG_FILE}")
else:
    logger.info(f"Appending to existing log file: {LOG_FILE}")

# Log interval in seconds (60 = 1 minute)
LOG_INTERVAL = 60

logger.info(f"Starting data logger - sampling every {LOG_INTERVAL} seconds")

try:
    while True:
        try:
            # Read all sensors
            data = sensors.read_all()
            
            # Read raw voltages
            v_pressure = sensors.read_voltage(1)  # A1
            v_water = sensors.read_voltage(0)     # A0
            v_air = sensors.read_voltage(2)       # A2
            
            # Calculate air sensor resistance from voltage
            if v_air >= sensors.V_SUPPLY - 0.01 or v_air < 0.01:
                r_air = 0.0
            else:
                r_air = (v_air * sensors.R_BIAS_AIR) / (sensors.V_SUPPLY - v_air)
            
            timestamp = datetime.now().isoformat()
            pressure = data.get('pressure_psi', 0.0)
            water_temp = data.get('temperature_f', 0.0)
            air_temp = data.get('air_temperature_f', 0.0)
            
            # Write to CSV with raw data
            with open(LOG_FILE, 'a') as f:
                f.write(f"{timestamp},{pressure:.2f},{v_pressure:.4f},{water_temp:.2f},{v_water:.4f},{air_temp:.2f},{v_air:.4f},{r_air:.2f}\n")
            
            logger.info(f"Logged: P={pressure:.1f}psi, Water={water_temp:.1f}°F, Air={air_temp:.1f}°F (A2={v_air:.3f}V, {r_air:.1f}Ω)")
            
        except Exception as e:
            logger.error(f"Error reading/logging sensors: {e}")
        
        time.sleep(LOG_INTERVAL)
        
except KeyboardInterrupt:
    logger.info("Data logger stopped by user")
except Exception as e:
    logger.error(f"Fatal error: {e}")
