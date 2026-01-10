#!/usr/bin/env python3
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c, address=0x48)
ads.gain = 1

print("Reading all ADS1115 channels:")
print("-" * 40)

for ch in range(4):
    chan = AnalogIn(ads, ch)
    print(f"A{ch}: {chan.voltage:.4f}V")

print("-" * 40)
