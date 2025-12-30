import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import logging
import math

logger = logging.getLogger(__name__)

class SensorManager:
    """Manager for ADS1115 ADC reading pressure and temperature sensors"""
    
    def __init__(self, i2c_address=0x48, gain=1):
        try:
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.ads = ADS.ADS1115(self.i2c, address=i2c_address)
            self.ads.gain = gain
            
            # Temperature sensor configuration (NTC thermistor with 1kΩ voltage divider)
            self.R_FIXED = 1000  # 1kΩ resistor from 3.3V
            self.V_SUPPLY = 3.3  # Supply voltage
            
            # Calibration point: 2.141V = 12277Ω = 65°F (18.3°C)
            self.CAL_VOLTAGE = 2.141
            self.CAL_TEMP_C = 18.3
            self.CAL_RESISTANCE = 12277
            
            # Estimated thermistor beta coefficient (typical for 10k NTC)
            # This can be refined with more calibration points
            self.BETA = 3950
            
            logger.info(f'ADS1115 initialized at address 0x{i2c_address:02X}, gain={gain}')
            
        except Exception as e:
            logger.error(f'Failed to initialize ADS1115: {e}')
            raise

    def read_voltage(self, channel):
        try:
            chan = AnalogIn(self.ads, channel)
            return chan.voltage
        except Exception as e:
            logger.error(f'Failed to read channel {channel}: {e}')
            return 0.0

    def read_pressure(self):
        # TEMP: Pressure sensor not connected yet
        """
        Read pressure from Channel 0.
        Sensor: PSU-GP100-6 (0-100 psi, 0-5V output)
        """
        voltage = self.read_voltage(1)
        psi = (voltage / 5.0) * 100.0
        return max(0.0, min(100.0, psi))

    def read_temperature(self):
        # Reading from A0 (thermistor with 1k voltage divider)
        """
        Read temperature from Channel 1.
        Uses NTC thermistor with 1kΩ voltage divider from 3.3V
        """
        voltage = self.read_voltage(0)
        
        # Avoid division by zero
        if voltage >= self.V_SUPPLY or voltage < 0.1:
            return self.CAL_TEMP_C * 9/5 + 32  # 65°F
        
        # Calculate thermistor resistance from voltage divider
        # V = V_supply * (R_therm / (R_therm + R_fixed))
        # R_therm = (V * R_fixed) / (V_supply - V)
        r_thermistor = (voltage * self.R_FIXED) / (self.V_SUPPLY - voltage)
        
        # Use simplified beta equation with calibration point
        # 1/T = 1/T0 + (1/B) * ln(R/R0)
        # T in Kelvin
        t0_kelvin = self.CAL_TEMP_C + 273.15
        
        try:
            temp_kelvin = 1.0 / (1.0/t0_kelvin + (1.0/self.BETA) * math.log(r_thermistor / self.CAL_RESISTANCE))
            temp_c = temp_kelvin - 273.15
            
            # Sanity check: water temp should be 0-100°C
            if temp_c < -10 or temp_c > 110:
                logger.warning(f'Temperature out of range: {temp_c:.1f}°C, using calibration value')
                return self.CAL_TEMP_C * 9/5 + 32  # 65°F
                
            return temp_c * 9/5 + 32  # Convert to Fahrenheit
            
        except Exception as e:
            logger.error(f'Temperature calculation error: {e}, R={r_thermistor:.0f}Ω, V={voltage:.3f}V')
            return self.CAL_TEMP_C * 9/5 + 32  # 65°F
    
    def read_all(self):
        return {
            'pressure_psi': self.read_pressure(),
            'temperature_f': self.read_temperature()
        }
