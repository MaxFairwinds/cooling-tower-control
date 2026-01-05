import logging
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VFDController:
    """Controller for a single VFD via Modbus RTU"""
    
    def __init__(self, client, device_id, description="VFD"):
        """
        Initialize VFD controller.
        
        Args:
            client: Shared ModbusSerialClient instance
            device_id: Modbus device ID (slave ID) for this VFD
            description: Human-readable description
        """
        self.client = client
        self.device_id = device_id
        self.description = description
        self.error_count = 0
        
        # TODO: Verify these register addresses with Galt G540 manual
        # Common defaults assumed below:
        self.REG_CONTROL = 0x2000  # Control Word
        self.REG_FREQ_SET = 0x2001 # Frequency Setpoint (0.01 Hz units usually)
        self.REG_STATUS = 0x2100   # Status Word
        self.REG_OUTPUT_FREQ = 0x2103 # Output Frequency

    def write_register(self, address, value):
        """Write a single register."""
        try:
            result = self.client.write_register(address, value, device_id=self.device_id)
            if result.isError():
                logger.error(f"[{self.description}] Error writing register {address}: {result}")
                self.error_count += 1
                return False
            self.error_count = 0  # Reset on success
            return True
        except ModbusException as e:
            logger.error(f"[{self.description}] Modbus exception: {e}")
            self.error_count += 1
            return False

    def read_register(self, address):
        """Read a single holding register."""
        try:
            result = self.client.read_holding_registers(address, count=1, device_id=self.device_id)
            if result.isError():
                logger.error(f"[{self.description}] Error reading register {address}: {result}")
                self.error_count += 1
                return None
            self.error_count = 0  # Reset on success
            return result.registers[0]
        except ModbusException as e:
            logger.error(f"[{self.description}] Modbus exception: {e}")
            self.error_count += 1
            return None

    def start(self):
        """Start the VFD (Forward Run)."""
        logger.info(f"[{self.description}] Sending START command")
        return self.write_register(self.REG_CONTROL, 0x0001)

    def stop(self):
        """Stop the VFD."""
        logger.info(f"[{self.description}] Sending STOP command")
        return self.write_register(self.REG_CONTROL, 0x0000)

    def set_frequency(self, hz):
        """Set frequency in Hz."""
        # Assuming 0.01 Hz resolution, so 50Hz = 5000
        value = int(hz * 100)
        logger.debug(f"[{self.description}] Setting frequency to {hz} Hz (Raw: {value})")
        return self.write_register(self.REG_FREQ_SET, value)

    def get_status(self):
        """Get VFD status and output frequency."""
        status = self.read_register(self.REG_STATUS)
        freq_raw = self.read_register(self.REG_OUTPUT_FREQ)
        
        freq = freq_raw / 100.0 if freq_raw is not None else 0.0
        
        return {
            "status_word": status,
            "output_frequency": freq,
            "healthy": self.error_count == 0
        }
    
    def is_healthy(self, max_errors=3):
        """Check if VFD is responding properly."""
        return self.error_count < max_errors


class MultiVFDManager:
    """Manager for multiple VFDs on the same RS-485 bus"""
    
    def __init__(self, port='/dev/ttyS0', baudrate=9600):
        """
        Initialize the multi-VFD manager.
        
        Args:
            port: Serial port path
            baudrate: Modbus baudrate
        """
        self.client = ModbusSerialClient(
            port=port,
            baudrate=baudrate,
            parity='N',
            stopbits=1,
            bytesize=8,
            timeout=1
        )
        self.vfds = {}
        
    def connect(self):
        """Connect to the Modbus serial port."""
        return self.client.connect()
    
    def close(self):
        """Close the connection."""
        self.client.close()
    
    def add_vfd(self, name, device_id, description):
        """
        Add a VFD to the manager.
        
        Args:
            name: Unique identifier for this VFD
            device_id: Modbus device ID
            description: Human-readable description
        """
        self.vfds[name] = VFDController(self.client, device_id, description)
        logger.info(f"Added VFD '{name}': {description} (Device ID: {device_id})")
    
    def get_vfd(self, name):
        """Get a VFD controller by name."""
        return self.vfds.get(name)
    
    def stop_all(self):
        """Stop all VFDs."""
        logger.info("Stopping all VFDs...")
        for name, vfd in self.vfds.items():
            vfd.stop()
