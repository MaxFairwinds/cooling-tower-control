import logging
import serial
import struct
import time

logger = logging.getLogger(__name__)

class VFDController:
    """Controller for GALT G540 VFD via Modbus RTU"""
    
    def __init__(self, ser, device_id, description="VFD"):
        """
        Initialize VFD controller.
        
        Args:
            ser: Shared serial.Serial instance
            device_id: Modbus device ID (slave ID) for this VFD
            description: Human-readable description
        """
        self.ser = ser
        self.device_id = device_id
        self.description = description
        self.error_count = 0
        
        # GALT G540 Register Map
        self.REG_CONTROL = 0x2000      # Control command
        self.REG_FREQ_SET = 0x2001     # Frequency setpoint (0.01 Hz units)
        self.REG_STATE_1 = 0x2100      # State word 1
        self.REG_STATE_2 = 0x2101      # State word 2
        self.REG_FAULT = 0x2102        # Fault code
        self.REG_RUN_FREQ = 0x3000     # Running frequency (0.01 Hz)
        self.REG_OUTPUT_CURRENT = 0x3004  # Output current (0.1 A)
        
        # Control commands
        self.CMD_FORWARD = 0x0001
        self.CMD_STOP = 0x0005
        self.CMD_FAULT_RESET = 0x0007

    def crc16(self, data):
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

    def write_register(self, register, value):
        """Write single register (function code 0x06)"""
        try:
            request = bytes([
                self.device_id,
                0x06,
                (register >> 8) & 0xFF,
                register & 0xFF,
                (value >> 8) & 0xFF,
                value & 0xFF
            ])
            request += self.crc16(request)
            
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self.ser.write(request)
            time.sleep(0.05)
            
            response = self.ser.read(256)
            
            if len(response) < 5:
                logger.error(f"[{self.description}] Write timeout")
                self.error_count += 1
                return False
            
            if response[-2:] != self.crc16(response[:-2]):
                logger.error(f"[{self.description}] Write CRC error")
                self.error_count += 1
                return False
            
            if response[1] & 0x80:
                logger.error(f"[{self.description}] Write exception: 0x{response[2]:02X}")
                self.error_count += 1
                return False
            
            self.error_count = 0
            return True
            
        except Exception as e:
            logger.error(f"[{self.description}] Write error: {e}")
            self.error_count += 1
            return False

    def read_register(self, register, count=1):
        """Read holding registers (function code 0x03)"""
        try:
            request = bytes([
                self.device_id,
                0x03,
                (register >> 8) & 0xFF,
                register & 0xFF,
                (count >> 8) & 0xFF,
                count & 0xFF
            ])
            request += self.crc16(request)
            
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
            self.ser.write(request)
            time.sleep(0.05)
            
            response = self.ser.read(256)
            
            if len(response) < 5:
                logger.error(f"[{self.description}] Read timeout")
                self.error_count += 1
                return None
            
            if response[-2:] != self.crc16(response[:-2]):
                logger.error(f"[{self.description}] Read CRC error")
                self.error_count += 1
                return None
            
            if response[1] & 0x80:
                logger.error(f"[{self.description}] Read exception: 0x{response[2]:02X}")
                self.error_count += 1
                return None
            
            byte_count = response[2]
            data = response[3:3+byte_count]
            
            values = []
            for i in range(0, len(data), 2):
                values.append((data[i] << 8) | data[i+1])
            
            self.error_count = 0
            return values if count > 1 else values[0]
            
        except Exception as e:
            logger.error(f"[{self.description}] Read error: {e}")
            self.error_count += 1
            return None

    def start(self):
        """Start the VFD (Forward Run)"""
        logger.info(f"[{self.description}] Sending START command")
        return self.write_register(self.REG_CONTROL, self.CMD_FORWARD)

    def stop(self):
        """Stop the VFD"""
        logger.info(f"[{self.description}] Sending STOP command")
        return self.write_register(self.REG_CONTROL, self.CMD_STOP)

    def set_frequency(self, hz):
        """
        Set frequency in Hz.
        
        Args:
            hz: Frequency in Hz (0-400)
        """
        # G540 uses 0.01 Hz units, so 50Hz = 5000
        value = int(hz * 100)
        logger.debug(f"[{self.description}] Setting frequency to {hz:.2f} Hz (raw: {value})")
        return self.write_register(self.REG_FREQ_SET, value)

    def get_status(self):
        """Get VFD status and measurements"""
        state1 = self.read_register(self.REG_STATE_1)
        run_freq = self.read_register(self.REG_RUN_FREQ)
        fault = self.read_register(self.REG_FAULT)
        current = self.read_register(self.REG_OUTPUT_CURRENT)
        
        # Decode state word 1
        state_map = {
            0x0001: "Forward",
            0x0002: "Reverse",
            0x0003: "Stopped",
            0x0004: "Fault",
            0x0005: "PowerOff",
            0x0006: "PreExcited"
        }
        
        return {
            "state": state_map.get(state1, "Unknown") if state1 else "NoComm",
            "output_frequency": (run_freq * 0.01) if run_freq else 0.0,
            "fault_code": fault if fault else 0,
            "output_current": (current * 0.1) if current else 0.0,
            "healthy": self.error_count == 0
        }
    
    def is_healthy(self, max_errors=3):
        """Check if VFD is responding properly"""
        return self.error_count < max_errors


class MultiVFDManager:
    """Manager for multiple GALT G540 VFDs on the same RS-485 bus"""
    
    def __init__(self, port='/dev/ttyUSB0', baudrate=19200, parity='E', stopbits=1, bytesize=8, timeout=1.0):
        """
        Initialize the multi-VFD manager.
        
        Args:
            port: Serial port path
            baudrate: Modbus baudrate (default 19200 for G540)
            parity: Parity ('E'=Even, 'O'=Odd, 'N'=None)
            stopbits: Stop bits (1 or 2)
            bytesize: Data bits (8)
            timeout: Serial timeout in seconds
        """
        parity_map = {'E': serial.PARITY_EVEN, 'O': serial.PARITY_ODD, 'N': serial.PARITY_NONE}
        
        self.ser = serial.serial_for_url(
            port,
            baudrate=baudrate,
            bytesize=bytesize,
            parity=parity_map.get(parity, serial.PARITY_EVEN),
            stopbits=stopbits,
            timeout=timeout
        )
        
        self.vfds = {}
        logger.info(f"Modbus RTU initialized: {port} @ {baudrate} baud, parity={parity}")
        
    def connect(self):
        """Connect to the Modbus serial port"""
        if self.ser.is_open:
            logger.info("Serial port already open")
            return True
        try:
            self.ser.open()
            logger.info("Serial port opened successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to open serial port: {e}")
            return False
    
    def close(self):
        """Close the connection"""
        self.ser.close()
        logger.info("Serial port closed")
    
    def add_vfd(self, name, device_id, description):
        """
        Add a VFD to the manager.
        
        Args:
            name: Unique identifier for this VFD
            device_id: Modbus device ID
            description: Human-readable description
        """
        self.vfds[name] = VFDController(self.ser, device_id, description)
        logger.info(f"Added VFD '{name}': {description} (Device ID: {device_id})")
    
    def get_vfd(self, name):
        """Get a VFD controller by name"""
        return self.vfds.get(name)
    
    def stop_all(self):
        """Stop all VFDs"""
        logger.info("Stopping all VFDs...")
        for name, vfd in self.vfds.items():
            vfd.stop()
