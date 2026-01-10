#!/usr/bin/env python3
"""
Read unknown sensor on ADS1115 A2 with 10k bias resistor to 3.3V
Continuously monitor voltage and resistance to help identify sensor type
"""

import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import time
import math

# Initialize I2C and ADS1115
i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c, address=0x48)
ads.gain = 1  # +/- 4.096V range

# A2 is channel 2
from adafruit_ads1x15.ads1x15 import Mode
chan = AnalogIn(ads, 2)

# Voltage divider configuration
R_BIAS = 10000  # 10kΩ bias resistor to 3.3V
V_SUPPLY = 3.3

print("=" * 60)
print("ADS1115 A2 Sensor Diagnostics")
print("=" * 60)
print(f"Configuration: {R_BIAS}Ω bias resistor to {V_SUPPLY}V")
print("Press Ctrl+C to stop")
print("-" * 60)
print(f"{'Time':<8} {'Voltage':<10} {'R_sensor':<12} {'Temp(°F)':<10} {'Notes':<20}")
print("-" * 60)

# For temperature calculations if it's a thermistor
BETA = 3950  # Typical for 10k NTC thermistor
R_REF = 10000  # Reference resistance at 25°C
T_REF = 25 + 273.15  # Reference temperature in Kelvin

try:
    sample_count = 0
    while True:
        voltage = chan.voltage
        
        # Calculate sensor resistance from voltage divider
        # V = V_supply * (R_sensor / (R_sensor + R_bias))
        # R_sensor = (V * R_bias) / (V_supply - V)
        
        if voltage >= V_SUPPLY - 0.01:
            r_sensor = float('inf')
            r_sensor_str = "∞ (open)"
        elif voltage < 0.01:
            r_sensor = 0
            r_sensor_str = "0Ω (short)"
        else:
            r_sensor = (voltage * R_BIAS) / (V_SUPPLY - voltage)
            
            # Format resistance nicely
            if r_sensor >= 1000:
                r_sensor_str = f"{r_sensor/1000:.2f}kΩ"
            else:
                r_sensor_str = f"{r_sensor:.0f}Ω"
        
        # Try to calculate temperature if it looks like a thermistor
        # (resistance in reasonable range 1k-100k)
        temp_f = None
        notes = ""
        
        if 1000 <= r_sensor <= 100000:
            try:
                # Beta equation: 1/T = 1/T0 + (1/B) * ln(R/R0)
                temp_kelvin = 1.0 / (1.0/T_REF + (1.0/BETA) * math.log(r_sensor / R_REF))
                temp_c = temp_kelvin - 273.15
                temp_f = temp_c * 9/5 + 32
                
                # Identify likely sensor type
                if 0 <= temp_c <= 100:
                    notes = "Likely NTC thermistor"
                elif temp_c < 0:
                    notes = "Cool/cold sensor"
                else:
                    notes = "Hot sensor"
                    
            except Exception as e:
                notes = f"Calc error: {e}"
        elif r_sensor < 100:
            notes = "Very low R - RTD?"
        elif r_sensor > 100000:
            notes = "High R - check wiring"
        else:
            notes = "Unknown sensor type"
        
        # Display reading
        temp_str = f"{temp_f:.1f}" if temp_f is not None else "N/A"
        
        print(f"{sample_count:<8} {voltage:<10.4f} {r_sensor_str:<12} {temp_str:<10} {notes:<20}")
        
        sample_count += 1
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\n" + "-" * 60)
    print("Diagnostic complete")
    print("\nSensor identification help:")
    print("  - NTC Thermistor: 10kΩ @ 25°C, resistance decreases with temp")
    print("  - RTD (Pt100): ~100Ω @ 0°C, increases with temp")
    print("  - RTD (Pt1000): ~1000Ω @ 0°C, increases with temp")
    print("  - Pressure sensor: Usually 4-20mA or voltage output (different wiring)")
    print("=" * 60)
