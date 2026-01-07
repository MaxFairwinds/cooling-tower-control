#!/usr/bin/env python3
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import time
import math

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c, address=0x48)
ads.gain = 1

chan = AnalogIn(ads, 2)

R_BIAS = 10000
V_SUPPLY = 3.3
BETA = 3950
R_REF = 10000
T_REF = 25 + 273.15

print("Reading A2 sensor...")
print("Sample | Voltage | Resistance | Temp(F)")
print("-" * 50)

for i in range(20):
    voltage = chan.voltage
    
    if voltage >= V_SUPPLY - 0.01:
        r_sensor = float('inf')
        print(f"{i:6} | {voltage:7.4f} | OPEN       | N/A")
    elif voltage < 0.01:
        r_sensor = 0
        print(f"{i:6} | {voltage:7.4f} | SHORT      | N/A")
    else:
        r_sensor = (voltage * R_BIAS) / (V_SUPPLY - voltage)
        
        if 1000 <= r_sensor <= 100000:
            try:
                temp_k = 1.0 / (1.0/T_REF + (1.0/BETA) * math.log(r_sensor / R_REF))
                temp_c = temp_k - 273.15
                temp_f = temp_c * 9/5 + 32
                print(f"{i:6} | {voltage:7.4f} | {r_sensor/1000:6.2f} kΩ | {temp_f:6.1f}")
            except:
                print(f"{i:6} | {voltage:7.4f} | {r_sensor/1000:6.2f} kΩ | ERROR")
        else:
            print(f"{i:6} | {voltage:7.4f} | {r_sensor:8.0f} Ω | N/A")
    
    time.sleep(0.5)

print("\nDone")
