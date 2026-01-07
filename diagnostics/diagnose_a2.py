#!/usr/bin/env python3
"""
Step-by-step A2 diagnostic to identify the issue
"""
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c, address=0x48)
ads.gain = 1

print("=" * 60)
print("A2 Sensor Diagnostic - Step by Step")
print("=" * 60)

# Read current state
chan2 = AnalogIn(ads, 2)
v_a2 = chan2.voltage

print(f"\nCurrent A2 reading: {v_a2:.4f}V")
print("\nThis suggests:")

if v_a2 < 0.1:
    print("  ❌ A2 is at ~0V (nearly ground)")
    print("\n  Possible causes:")
    print("  1. Sensor is an ACTIVE device outputting low voltage")
    print("     (e.g., 4-20mA pressure sensor, powered transducer)")
    print("  2. Sensor has very low resistance (<100Ω)")
    print("  3. A2 is shorted to ground somewhere")
    print("  4. Bias resistor not actually connected to A2")
    
elif 0.1 <= v_a2 < 1.0:
    r_sensor = (v_a2 * 10000) / (3.3 - v_a2)
    print(f"  ✓ Sensor resistance: ~{r_sensor:.0f}Ω ({r_sensor/1000:.1f}kΩ)")
    print("  Sensor appears to be working!")
    
elif 1.0 <= v_a2 < 3.0:
    r_sensor = (v_a2 * 10000) / (3.3 - v_a2)
    print(f"  ✓ Sensor resistance: ~{r_sensor:.0f}Ω ({r_sensor/1000:.1f}kΩ)")
    print("  Sensor appears to be working!")
    
elif v_a2 >= 3.0:
    print("  ⚠️  A2 is at ~3.3V (pulled high)")
    print("  This means bias resistor is connected but sensor is OPEN")
    print("  Check sensor wiring to GND")

print("\n" + "=" * 60)
print("TROUBLESHOOTING STEPS:")
print("=" * 60)

print("\n1. With everything connected (current state):")
print(f"   A2 = {v_a2:.4f}V")

print("\n2. Please try:")
print("   a) Disconnect the sensor wires completely from A2/GND")
print("      (leave only the 10kΩ bias resistor)")
print("   b) Run this script again")
print("   c) You should see ~3.3V if bias resistor is connected")

print("\n3. Then reconnect ONLY ONE sensor wire to GND and check:")
print("   - If sensor is resistive, voltage should drop")
print("   - If sensor is active/powered, behavior may be different")

print("\n4. Check what type of sensor this is:")
print("   - Thermistor/RTD: Passive resistive sensor")
print("   - Pressure transducer: Often powered (4-20mA or 0-5V)")
print("   - Hall effect: Needs power, outputs voltage")
print("   - If it has 3+ wires, it's probably an active sensor")

print("\n" + "=" * 60)
