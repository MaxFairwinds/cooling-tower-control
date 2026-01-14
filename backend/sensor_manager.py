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
    
    def read_all(self):
        """Read all sensors and return current values plus statistics"""
        # Read raw values (also populates buffers)
        current_pressure = self.read_pressure()
        current_temp = self.read_temperature()
        current_flow = self.read_flow_gpm()
        
        # Calculate statistics from buffers
        pressure_avg, pressure_std = self._calc_stats(self.pressure_buffer)
        temp_avg, temp_std = self._calc_stats(self.temp_buffer)
        flow_avg, flow_std = self._calc_stats(self.flow_buffer)
        
        return {
            'pressure_psi': pressure_avg,
            'pressure_std': pressure_std,
            'temperature_f': temp_avg,
            'temperature_std': temp_std,
            'flow_gpm': flow_avg,
            'flow_std': flow_std
        }
