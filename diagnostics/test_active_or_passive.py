#!/usr/bin/env python3
"""
Test to determine if sensor is ACTIVE (outputs voltage) or PASSIVE (resistive)
"""
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c, address=0x48)
ads.gain = 1

print("=" * 60)
print("IS THE SENSOR ACTIVE OR PASSIVE?")
print("=" * 60)

chan2 = AnalogIn(ads, 2)
v_a2 = chan2.voltage

print(f"\nCurrent A2 reading: {v_a2:.4f}V")

print("\n" + "=" * 60)
print("NEXT STEPS - Please do this:")
print("=" * 60)

print("\n1. TEMPORARILY DISCONNECT the 10kΩ bias resistor from A2")
print("   (Just remove the resistor lead from A2, leave sensor connected)")

print("\n2. Run this script again")

print("\n3. Check the voltage:")
print("   - If voltage stays ~3V → ACTIVE sensor (outputs its own voltage)")
print("   - If voltage drops to ~0V → PASSIVE sensor (just resistance)")

print("\n" + "=" * 60)
print("INTERPRETATION:")
print("=" * 60)

print("\nACTIVE sensor (3-wire pressure transducer, hall effect, etc):")
print("  - Has power wire, ground wire, signal wire")
print("  - Outputs 0-5V or 0-10V or 4-20mA")
print("  - Does NOT need bias resistor")
print("  - Connect signal wire directly to A2, no resistor needed")

print("\nPASSIVE sensor (thermistor, RTD, etc):")
print("  - Just 2 wires")
print("  - Only has resistance, no voltage output")
print("  - NEEDS bias resistor to create voltage divider")

print("\n" + "=" * 60)
