import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
from adafruit_extended_bus import ExtendedI2C as I2C
import logging
import math
import glob
import os
from collections import deque
import statistics

logger = logging.getLogger(__name__)

class SensorManager:
    """Manager for ADS1115 ADC reading pressure and temperature sensors"""
    
    def __init__(self, i2c_address=0x48, gain=1):
        try:
            # Auto-detect which I2C bus the ADS1115 is on
            self.i2c = None
            i2c_buses = sorted([int(os.path.basename(f).split('-')[1]) for f in glob.glob('/dev/i2c-*')])
            
            for bus_num in i2c_buses:
                try:
                    test_i2c = I2C(bus_num)
                    test_ads = ADS.ADS1115(test_i2c, address=i2c_address)
                    # Successfully connected
                    self.i2c = test_i2c
                    self.ads = test_ads
                    logger.info(f'ADS1115 found on I2C bus {bus_num} at address 0x{i2c_address:02X}')
                    break
                except Exception as e:
                    continue
            
            if self.i2c is None:
                raise Exception(f'No I2C device at address: 0x{i2c_address:02X}')
            self.ads.gain = gain
            
            # Temperature sensor configuration (NTC thermistor with 10kΩ voltage divider)
            self.R_FIXED = 10000  # 10kΩ resistor from 3.3V
            self.V_SUPPLY = 3.3  # Supply voltage
            
            # Calibration: measured 1.827V at 63°F (17.2°C)
            # Thermistor measured at 14kΩ (voltage divider: 3.3V × 14k/24k = 1.925V theoretical)
            # Using actual measured voltage for calibration
            self.CAL_VOLTAGE = 1.827
            self.CAL_TEMP_C = 17.2  # 63°F
            # Calculate resistance from measured voltage
            self.CAL_RESISTANCE = (1.827 * 10000) / (3.3 - 1.827)  # ≈12.4kΩ
            
            # Beta coefficient - adjust if needed with second calibration point
            self.BETA = 3950
            
            # Return water temperature sensor (A3) - same thermistor/resistor as basin temp
            # Reading 1.925V at ~67°F ambient (19.4°C)
            # Calculated resistance: (1.925 × 10k) / (3.3 - 1.925) = 14,000Ω
            # Will measure outlet/return water temp when installed
            self.RETURN_CAL_VOLTAGE = 1.925
            self.RETURN_CAL_TEMP_C = 19.4  # 67°F
            self.RETURN_CAL_RESISTANCE = 14000  # Calculated from voltage divider
            
            # Air temperature RTD configuration (100Ω bias resistor)
            # Measures air temp INSIDE cooling tower (above water level)
            self.R_BIAS_AIR = 100.0  # 100Ω bias resistor for RTD
            # Calibration: 87Ω = ~70°F estimated (verify with thermometer)
            self.CAL_RTD_RESISTANCE = 87.0
            self.CAL_RTD_TEMP_F = 70.0  # Estimated - measure actual temp to calibrate
            
            # Rolling buffers for 5-second moving average (10 samples at 2 Hz)
            self.pressure_buffer = deque(maxlen=10)
            self.temp_buffer = deque(maxlen=10)
            self.flow_buffer = deque(maxlen=10)
            self.return_temp_buffer = deque(maxlen=10)
            
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
    
    def _calc_stats(self, buffer):
        """Calculate average and standard deviation from buffer"""
        if len(buffer) == 0:
            return 0.0, 0.0
        avg = statistics.mean(buffer)
        stddev = statistics.stdev(buffer) if len(buffer) > 1 else 0.0
        return avg, stddev

    def read_pressure(self):
        # TEMP: Pressure sensor not connected yet
        """
        Read pressure from Channel 0.
        Sensor: PSU-GP100-6 (0-100 psi, 0-5V output)
        """
        voltage = self.read_voltage(1)
        psi = (voltage / 5.0) * 100.0
        psi = max(0.0, min(100.0, psi))
        
        # Add to rolling buffer
        self.pressure_buffer.append(psi)
        
        return psi

    def read_flow_gpm(self):
        """
        Read flow rate from A2 pin (Channel 2)
        Omega flow meter: 4-20mA output, 0-1000 GPM range
        150 ohm current sensing resistor:
          4mA = 0.6V = 0 GPM
          20mA = 3.0V = 1000 GPM
        """
        voltage = self.read_voltage(2)
        
        # 4-20mA to GPM conversion
        V_MIN = 0.6   # 4mA × 150Ω
        V_MAX = 3.0   # 20mA × 150Ω
        GPM_MAX = 1000.0
        
        if voltage < V_MIN:
            gpm = 0.0
        else:
            gpm = (voltage - V_MIN) / (V_MAX - V_MIN) * GPM_MAX
            gpm = max(0.0, min(GPM_MAX, gpm))
        
        # Add to rolling buffer
        self.flow_buffer.append(gpm)
        
        return gpm
    
    def read_temperature(self):
        # Reading from A0 (thermistor with 1k voltage divider)
        """
        Read water temperature from Channel 0 (A0).
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
                temp_f = self.CAL_TEMP_C * 9/5 + 32  # 65°F
            else:
                temp_f = temp_c * 9/5 + 32  # Convert to Fahrenheit
            
            # Add to rolling buffer
            self.temp_buffer.append(temp_f)
            
            return temp_f
                
        except Exception as e:
            logger.error(f'Temperature calculation error: {e}, R={r_thermistor:.0f}Ω, V={voltage:.3f}V')
            temp_f = self.CAL_TEMP_C * 9/5 + 32  # 65°F
            self.temp_buffer.append(temp_f)
            return temp_f
    
    def read_return_temperature(self):
        """
        Read return water temperature from Channel 3 (A3).
        Same NTC thermistor with 10kΩ voltage divider as basin temp
        """
        voltage = self.read_voltage(3)
        
        # Avoid division by zero
        if voltage >= self.V_SUPPLY or voltage < 0.1:
            return self.RETURN_CAL_TEMP_C * 9/5 + 32
        
        # Calculate thermistor resistance from voltage divider
        r_thermistor = (voltage * self.R_FIXED) / (self.V_SUPPLY - voltage)
        
        # Use simplified beta equation with return sensor calibration point
        t0_kelvin = self.RETURN_CAL_TEMP_C + 273.15
        
        try:
            temp_kelvin = 1.0 / (1.0/t0_kelvin + (1.0/self.BETA) * math.log(r_thermistor / self.RETURN_CAL_RESISTANCE))
            temp_c = temp_kelvin - 273.15
            
            # Sanity check: water temp should be 0-100°C
            if temp_c < -10 or temp_c > 110:
                logger.warning(f'Return temp out of range: {temp_c:.1f}°C, using calibration value')
                temp_f = self.RETURN_CAL_TEMP_C * 9/5 + 32
            else:
                temp_f = temp_c * 9/5 + 32  # Convert to Fahrenheit
            
            # Add to rolling buffer
            self.return_temp_buffer.append(temp_f)
            
            return temp_f
                
        except Exception as e:
            logger.error(f'Return temp calculation error: {e}, R={r_thermistor:.0f}Ω, V={voltage:.3f}V')
            temp_f = self.RETURN_CAL_TEMP_C * 9/5 + 32
            self.return_temp_buffer.append(temp_f)
            return temp_f
    
    def read_all(self):
        """Read all sensors and return current values plus statistics"""
        # Read raw values (also populates buffers)
        current_pressure = self.read_pressure()
        current_temp = self.read_temperature()
        current_flow = self.read_flow_gpm()
        current_return_temp = self.read_return_temperature()
        
        # Calculate statistics from buffers
        pressure_avg, pressure_std = self._calc_stats(self.pressure_buffer)
        temp_avg, temp_std = self._calc_stats(self.temp_buffer)
        flow_avg, flow_std = self._calc_stats(self.flow_buffer)
        return_temp_avg, return_temp_std = self._calc_stats(self.return_temp_buffer)
        
        return {
            'pressure_psi': pressure_avg,
            'pressure_std': pressure_std,
            'temperature_f': temp_avg,
            'temperature_std': temp_std,
            'flow_gpm': flow_avg,
            'flow_std': flow_std,
            'return_temp_f': return_temp_avg,
            'return_temp_std': return_temp_std
        }
