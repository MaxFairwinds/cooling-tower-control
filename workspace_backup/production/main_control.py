import time
import logging
from vfd_controller import MultiVFDManager
from sensor_manager import SensorManager
from pump_failover import PumpFailoverManager
from config import *

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CoolingTowerController:
    """Main controller for cooling tower system with 3 VFDs"""
    
    def __init__(self):
        # Initialize VFD manager
        self.vfd_manager = MultiVFDManager(SERIAL_PORT, SERIAL_BAUDRATE)
        
        # Add VFDs
        for name, cfg in VFD_CONFIG.items():
            self.vfd_manager.add_vfd(name, cfg['device_id'], cfg['description'])
        
        # Get VFD references
        self.fan_vfd = self.vfd_manager.get_vfd('fan')
        pump_primary = self.vfd_manager.get_vfd('pump_primary')
        pump_backup = self.vfd_manager.get_vfd('pump_backup')
        
        # Initialize pump failover manager
        self.pump_manager = PumpFailoverManager(
            pump_primary,
            pump_backup,
            max_errors=PUMP_FAILOVER['max_consecutive_errors'],
            check_interval=PUMP_FAILOVER['health_check_interval']
        )
        
        # Initialize sensors
        self.sensors = SensorManager()
        
        self.running = False
        
    def run(self):
        """Main control loop"""
        logger.info("="*60)
        logger.info("Starting Cooling Tower Control System")
        logger.info("Configuration:")
        logger.info(f"  Fan VFD: Device ID {VFD_CONFIG['fan']['device_id']}")
        logger.info(f"  Pump Primary: Device ID {VFD_CONFIG['pump_primary']['device_id']}")
        logger.info(f"  Pump Backup: Device ID {VFD_CONFIG['pump_backup']['device_id']}")
        logger.info(f"  Target Pressure: {CONTROL_PARAMS['target_pressure']} psi")
        logger.info("="*60)
        
        if not self.vfd_manager.connect():
            logger.error("Failed to connect to Modbus")
            return

        try:
            self.running = True
            
            # Start fan (could be constant speed or variable)
            # For now, set to a fixed frequency
            logger.info("Starting fan motor...")
            self.fan_vfd.start()
            self.fan_vfd.set_frequency(45.0)  # 45 Hz for fan
            
            # Start primary pump
            logger.info("Starting primary pump...")
            self.pump_manager.get_active_vfd().start()
            
            while self.running:
                # Read sensors
                pressure = self.sensors.read_pressure()
                temp = self.sensors.read_temperature()
                
                # Check pump health and failover if needed
                if PUMP_FAILOVER['auto_failover_enabled']:
                    self.pump_manager.check_health()
                
                # Control Logic (Simple P-Controller for pump)
                error = CONTROL_PARAMS['target_pressure'] - pressure
                output_hz = 30.0 + (error * CONTROL_PARAMS['kp'])
                
                # Clamp frequency
                output_hz = max(
                    CONTROL_PARAMS['min_frequency'],
                    min(CONTROL_PARAMS['max_frequency'], output_hz)
                )
                
                # Update pump frequency
                self.pump_manager.set_frequency(output_hz)
                
                # Get status
                fan_status = self.fan_vfd.get_status()
                pump_status = self.pump_manager.get_status()
                
                # Log status
                logger.info(
                    f"P: {pressure:.2f}psi, T: {temp:.2f}°C | "
                    f"Pump: {pump_status['active_pump']} @ {output_hz:.1f}Hz | "
                    f"Fan: {fan_status['output_frequency']:.1f}Hz"
                )
                
                time.sleep(1.0)
                
        except KeyboardInterrupt:
            logger.info("Stopping system (Ctrl+C)...")
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
        finally:
            self._shutdown()
    
    def _shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down...")
        self.pump_manager.stop()
        self.fan_vfd.stop()
        self.vfd_manager.stop_all()
        self.vfd_manager.close()
        logger.info("System stopped")

if __name__ == "__main__":
    controller = CoolingTowerController()
    controller.run()
