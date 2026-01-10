import board, busio, time
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c, address=0x48)
ads.gain = 1
chan = AnalogIn(ads, 2)

print('A2 Sensor Test - Checking for changes...')
print('Reading voltage for 20 seconds...')
print()

readings = []
for i in range(40):
    v = chan.voltage
    readings.append(v)
    print(f'{i:2d}s: {v:.4f}V', end='')
    if i > 0:
        change = abs(v - readings[i-1])
        if change > 0.01:
            print(f'  <- CHANGED by {change:.4f}V!')
        else:
            print()
    else:
        print()
    time.sleep(0.5)

print()
print(f'Min: {min(readings):.4f}V')
print(f'Max: {max(readings):.4f}V')
print(f'Range: {max(readings) - min(readings):.4f}V')
print()
print('CONCLUSION:')
if max(readings) - min(readings) < 0.01:
    print('-> Voltage is CONSTANT (< 0.01V variation)')
    print('-> Likely a fixed resistor or inactive sensor')
else:
    print('-> Voltage is CHANGING')
    print('-> Active sensor responding to something')
