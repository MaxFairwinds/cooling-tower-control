import logging
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException

logger = logging.getLogger(__name__)

class CFW300Controller:
    """
    VFD Controller specifically for WEG CFW300 drives.
    
    Uses CFW300-specific register map and scaling.
    Separate from production G540 controller to avoid confusion.
    """
    
    def __init__(self, client, device_id, description="CFW300", rated_freq=60.0):
        """
        Initialize CFW300 controller.
        
        Args:
            client: Shared ModbusSerialClient instance
            device_id: Modbus device ID (101-103 for test environment)
            description: Human-readable description
            rated_freq: Motor rated frequency in Hz (match P403 on drive)
        """
        self.client = client
        self.device_id = device_id
        self.description = description
        self.rated_freq = rated_freq
        self.error_count = 0
        
        # CFW300 Register Addresses (Parameters)
        self.REG_CONTROL_WORD = 682    # P682
        self.REG_SPEED_REF = 681       # P681
        self.REG_STATUS_WORD = 683     # P683
        self.REG_FAULT_CODE = 48       # P048
        
        # Control word bits
        self.BIT_RUN_FORWARD = 0x0001
        self.BIT_RUN_REVERSE = 0x0002
        self.BIT_ENABLE = 0x0200
        self.BIT_FAULT_RESET = 0x0080
        
        # Speed scaling constant (13-bit)
        self.SPEED_SCALE_MAX = 8191

    def write_register(self, address, value):
        """Write a single register (parameter)."""
        try:
            result = self.client.write_register(address, value, device_id=self.device_id)
            if result.isError():
                logger.error(f"[{self.description}] Error writing P{address}: {result}")
                self.error_count += 1
                return False
            self.error_count = 0
            logger.debug(f"[{self.description}] Wrote P{address} = {value}")
            return True
        except ModbusException as e:
            logger.error(f"[{self.description}] Modbus exception: {e}")
            self.error_count += 1
            return False

    def read_register(self, address):
        """Read a single register (parameter)."""
        try:
            result = self.client.read_holding_registers(address, count=1, device_id=self.device_id)
            if result.isError():
                logger.error(f"[{self.description}] Error reading P{address}: {result}")
                self.error_count += 1
                return None
            self.error_count = 0
            value = result.registers[0]
            logger.debug(f"[{self.description}] Read P{address} = {value}")
            return value
        except ModbusException as e:
            logger.error(f"[{self.description}] Modbus exception: {e}")
            self.error_count += 1
            return None

    def hz_to_scaled(self, hz):
        """
        Convert frequency in Hz to CFW300 scaled value.
        
        CFW300 uses 13-bit scaling: 0-8191 maps to 0-rated_freq
        Example: For 60Hz rated, 30Hz = 4096 (half of 8191)
        """
        if hz < 0:
            hz = 0
        if hz > self.rated_freq:
            hz = self.rated_freq
        scaled = int((hz / self.rated_freq) * self.SPEED_SCALE_MAX)
        return scaled

    def scaled_to_hz(self, scaled):
        """Convert CFW300 scaled value to frequency in Hz."""
        hz = (scaled / self.SPEED_SCALE_MAX) * self.rated_freq
        return hz

    def start_forward(self):
        """Start the VFD in forward direction."""
        logger.info(f"[{self.description}] Starting FORWARD")
        control_word = self.BIT_RUN_FORWARD | self.BIT_ENABLE
        return self.write_register(self.REG_CONTROL_WORD, control_word)

    def start_reverse(self):
        """Start the VFD in reverse direction."""
        logger.info(f"[{self.description}] Starting REVERSE")
        control_word = self.BIT_RUN_REVERSE | self.BIT_ENABLE
        return self.write_register(self.REG_CONTROL_WORD, control_word)

    def stop(self):
        """Stop the VFD."""
        logger.info(f"[{self.description}] Stopping")
        return self.write_register(self.REG_CONTROL_WORD, 0x0000)

    def reset_fault(self):
        """Reset fault condition."""
        logger.info(f"[{self.description}] Resetting fault")
        control_word = self.BIT_FAULT_RESET
        return self.write_register(self.REG_CONTROL_WORD, control_word)

    def set_frequency(self, hz):
        """
        Set frequency setpoint in Hz.
        
        Args:
            hz: Desired frequency in Hz (0 to rated_freq)
        """
        scaled = self.hz_to_scaled(hz)
        logger.info(f"[{self.description}] Setting frequency to {hz:.2f} Hz (scaled: {scaled})")
        return self.write_register(self.REG_SPEED_REF, scaled)

    def get_status(self):
        """Get VFD status."""
        status_word = self.read_register(self.REG_STATUS_WORD)
        speed_scaled = self.read_register(self.REG_SPEED_REF)
        fault_code = self.read_register(self.REG_FAULT_CODE)
        
        speed_hz = self.scaled_to_hz(speed_scaled) if speed_scaled is not None else 0.0
        
        return {
            "status_word": status_word,
            "speed_hz": speed_hz,
            "speed_scaled": speed_scaled,
            "fault_code": fault_code,
            "healthy": self.error_count == 0
        }
    
    def is_healthy(self, max_errors=3):
        """Check if VFD is responding properly."""
        return self.error_count < max_errors


class CFW300Manager:
    """Manager for multiple CFW300 VFDs on the same RS-485 bus"""
    
    def __init__(self, port='/dev/ttyS0', baudrate=9600, rated_freq=60.0):
        """
        Initialize the CFW300 manager.
        
        Args:
            port: Serial port path
            baudrate: Modbus baudrate (match P301 on CFW300)
            rated_freq: Motor rated frequency (match P403 on CFW300)
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
        self.rated_freq = rated_freq
        
    def connect(self):
        """Connect to the Modbus serial port."""
        return self.client.connect()
    
    def close(self):
        """Close the connection."""
        self.client.close()
    
    def add_vfd(self, name, device_id, description):
        """
        Add a CFW300 VFD to the manager.
        
        Args:
            name: Unique identifier for this VFD
            device_id: Modbus device ID (101-103 for test)
            description: Human-readable description
        """
        self.vfds[name] = CFW300Controller(
            self.client, 
            device_id, 
            description,
            self.rated_freq
        )
        logger.info(f"Added CFW300 '{name}': {description} (Device ID: {device_id})")
    
    def get_vfd(self, name):
        """Get a VFD controller by name."""
        return self.vfds.get(name)
    
    def stop_all(self):
        """Stop all VFDs."""
        logger.info("Stopping all CFW300 VFDs...")
        for name, vfd in self.vfds.items():
            vfd.stop()
