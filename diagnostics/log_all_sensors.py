#!/usr/bin/env python3
"""
Continuous data logging for RTD sensor on A2
Logs timestamp, voltage, and resistance to help identify what it measures
"""

import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import time
from datetime import datetime

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c, address=0x48)
ads.gain = 1

# Read all channels for comparison
chan0 = AnalogIn(ads, 0)  # Water temp thermistor
chan1 = AnalogIn(ads, 1)  # Pressure
chan2 = AnalogIn(ads, 2)  # RTD sensor

R_BIAS_A0 = 1000.0  # 1k for thermistor
R_BIAS_A2 = 100.0   # 100Ω for RTD
V_SUPPLY = 3.3

print("=" * 80)
print("Multi-Channel Sensor Data Logger")
print("=" * 80)
print("Logging A0 (water temp), A1 (pressure), A2 (RTD) to identify A2 sensor")
print("-" * 80)
print(f"{'Time':<20} {'A0(V)':<8} {'A0(kΩ)':<8} {'A1(V)':<8} {'A2(V)':<8} {'A2(Ω)':<8}")
print("-" * 80)

try:
    while True:
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        v0 = chan0.voltage
        v1 = chan1.voltage
        v2 = chan2.voltage
        
        # Calculate thermistor resistance on A0
        if 0.1 < v0 < 3.2:
            r0 = (v0 * R_BIAS_A0) / (V_SUPPLY - v0)
            r0_str = f"{r0/1000:.2f}"
        else:
            r0_str = "N/A"
        
        # Calculate RTD resistance on A2
        if 0.1 < v2 < 3.2:
            r2 = (v2 * R_BIAS_A2) / (V_SUPPLY - v2)
            r2_str = f"{r2:.1f}"
        else:
            r2_str = "N/A"
        
        print(f"{timestamp:<20} {v0:<8.4f} {r0_str:<8} {v1:<8.4f} {v2:<8.4f} {r2_str:<8}")
        
        time.sleep(5)  # Log every 5 seconds
        
except KeyboardInterrupt:
    print("\n" + "-" * 80)
    print("Logging stopped")
    print("\nAnalysis tips:")
    print("  - If A2 changes with A0: RTD measures water temperature")
    print("  - If A2 stable while A0 changes: RTD measures ambient/air temp")
    print("  - If A2 changes slowly: RTD has thermal mass (pipe, outdoor air)")
    print("  - Compare resistance range to identify sensor type")
    print("=" * 80)
