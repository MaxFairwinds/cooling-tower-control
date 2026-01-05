import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

class SensorManager:
    def __init__(self):
        # Create the I2C bus
        self.i2c = busio.I2C(board.SCL, board.SDA)
        
        # Create the ADC object using the I2C bus
        self.ads = ADS.ADS1115(self.i2c)
        
        # Configure gain if needed (default is 1, +/- 4.096V)
        # Pressure sensor is 0-5V, so we might need a voltage divider or adjust gain/wiring.
        # If using 5V sensor on 3.3V Pi logic, a divider is needed.
        # Assuming divider scales 5V -> 3.3V or similar, or ADS1115 is powered by 5V (but i2c logic levels matter).
        # ADS1115 can handle up to VDD + 0.3V.
        # If ADS1115 VDD=5V, it can read 5V, but SDA/SCL need level shifting for Pi (3.3V).
        # If ADS1115 VDD=3.3V, max input is 3.3V.
        
        # Assuming standard setup: ADS1115 VDD=3.3V, Pressure signal divided 2/3 or similar.
        # For now, we read raw voltage and scale.
        self.ads.gain = 1

    def read_voltage(self, channel):
        """Read voltage from a channel (0-3)."""
        chan = AnalogIn(self.ads, channel)
        return chan.voltage

    def read_pressure(self):
        """
        Read pressure from Channel 0.
        Sensor: PSU-GP100-6 (0-100 psi, 0-5V output).
        """
        voltage = self.read_voltage(0)
        
        # Scaling logic:
        # If 0-5V maps to 0-100 psi
        # But if we have a voltage divider (e.g. 5V -> 3.3V max), we need to account for it.
        # Assuming direct 0-5V for now (WARNING: Check input voltage limits!)
        # or assuming the user has handled the electrical side as per overview.
        
        # Simple linear mapping: 0.5V = 0 psi, 4.5V = 100 psi (common ratiometric)
        # Or 0V = 0 psi, 5V = 100 psi.
        # Overview says "0-5 V, 0-100 psi".
        
        psi = (voltage / 5.0) * 100.0
        return max(0.0, psi)

    def read_temperature(self):
        """
        Read temperature from Channel 1.
        Placeholder logic.
        """
        voltage = self.read_voltage(1)
        # Placeholder conversion
        temp_c = voltage * 10.0 # Dummy
        return temp_c
