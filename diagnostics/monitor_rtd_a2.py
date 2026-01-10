#!/usr/bin/env python3
"""
Monitor RTD sensor on A2 with 100Ω bias resistor
Shows raw voltage and resistance - temperature TBD after calibration
"""

import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import time

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c, address=0x48)
ads.gain = 1
chan = AnalogIn(ads, 2)

R_BIAS = 100.0  # 100Ω bias resistor
V_SUPPLY = 3.3

print("=" * 60)
print("RTD Sensor Monitor (A2 with 100Ω bias)")
print("=" * 60)
print(f"{'Time':<8} {'Voltage':<10} {'R_RTD (Ω)':<12} {'Notes':<20}")
print("-" * 60)

try:
    sample = 0
    while True:
        v = chan.voltage
        
        if v >= V_SUPPLY - 0.01:
            print(f"{sample:<8} {v:<10.4f} {'OPEN':<12} {'Check wiring':<20}")
        elif v < 0.01:
            print(f"{sample:<8} {v:<10.4f} {'SHORT':<12} {'Check wiring':<20}")
        else:
            r_rtd = (v * R_BIAS) / (V_SUPPLY - v)
            print(f"{sample:<8} {v:<10.4f} {r_rtd:<12.2f}")
        
        sample += 1
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\n" + "-" * 60)
    print("Monitoring stopped")
    print("\nTo calibrate: measure actual temperature and note the resistance")
    print("=" * 60)
