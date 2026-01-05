import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import logging

logger = logging.getLogger(__name__)

class SensorManager:
    """Manager for ADS1115 ADC reading pressure and temperature sensors"""
    
    def __init__(self, i2c_address=0x48, gain=1):
        """
        Initialize sensor manager.
        
        Args:
            i2c_address: I2C address of ADS1115 (default 0x48)
            gain: ADS1115 gain setting (default 1 = +/- 4.096V)
        """
        try:
            # Create the I2C bus
            self.i2c = busio.I2C(board.SCL, board.SDA)
            
            # Create the ADC object using the I2C bus
            self.ads = ADS.ADS1115(self.i2c, address=i2c_address)
            
            # Configure gain
            # Gain 1 = +/- 4.096V (default)
            # NOTE: If using 0-5V sensors, ensure proper voltage divider
            # or power ADS1115 with 5V instead of 3.3V
            self.ads.gain = gain
            
            logger.info(f"ADS1115 initialized at address 0x{i2c_address:02X}, gain={gain}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ADS1115: {e}")
            raise

    def read_voltage(self, channel):
        """
        Read voltage from a channel (0-3).
        
        Args:
            channel: ADS1115 channel number (0-3)
            
        Returns:
            Voltage in volts
        """
        try:
            chan = AnalogIn(self.ads, channel)
            return chan.voltage
        except Exception as e:
            logger.error(f"Failed to read channel {channel}: {e}")
            return 0.0

    def read_pressure(self):
        """
        Read pressure from Channel 0.
        
        Sensor: PSU-GP100-6 (0-100 psi, 0-5V output)
        
        Returns:
            Pressure in PSI
        """
        voltage = self.read_voltage(0)
        
        # Linear mapping: 0V = 0 psi, 5V = 100 psi
        # If using voltage divider (5V -> 3.3V), adjust scaling:
        # voltage_actual = voltage * (5.0 / 3.3) if divider used
        
        # Assuming direct 0-5V reading (ADS1115 powered at 5V)
        # or appropriate voltage divider already in place
        psi = (voltage / 5.0) * 100.0
        
        return max(0.0, min(100.0, psi))  # Clamp to 0-100 psi

    def read_temperature(self):
        """
        Read temperature from Channel 1.
        
        TODO: Update conversion formula based on actual sensor type
        
        Returns:
            Temperature in Celsius
        """
        voltage = self.read_voltage(1)
        
        # Placeholder conversion - UPDATE THIS based on your sensor
        # Common examples:
        # - LM35: 10mV/°C (0-100°C = 0-1V)
        # - TMP36: 750mV @ 25°C, 10mV/°C
        # - Thermocouple with amp: varies by model
        
        # Example for LM35 (10mV = 1°C):
        temp_c = voltage * 100.0
        
        return temp_c
    
    def read_all(self):
        """
        Read all sensors.
        
        Returns:
            Dictionary with pressure and temperature
        """
        return {
            'pressure_psi': self.read_pressure(),
            'temperature_c': self.read_temperature()
        }
