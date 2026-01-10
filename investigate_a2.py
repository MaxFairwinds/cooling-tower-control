import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('sensor_data.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)

print('='*80)
print('A2 SENSOR INVESTIGATION - WHAT IS IT REALLY MEASURING?')
print('='*80)

print('\n📊 A2 RAW VOLTAGE BEHAVIOR:')
print(f'   Average:  {df["air_voltage"].mean():.4f} V')
print(f'   Min:      {df["air_voltage"].min():.4f} V')
print(f'   Max:      {df["air_voltage"].max():.4f} V')
print(f'   Range:    {df["air_voltage"].max() - df["air_voltage"].min():.4f} V')
print(f'   Std Dev:  {df["air_voltage"].std():.4f} V')
print(f'   Coefficient of Variation: {(df["air_voltage"].std() / df["air_voltage"].mean() * 100):.2f}%')

print('\n📊 COMPARE TO WATER TEMP VOLTAGE:')
print(f'   Water voltage avg:    {df["water_voltage"].mean():.4f} V')
print(f'   Water voltage range:  {df["water_voltage"].max() - df["water_voltage"].min():.4f} V')
print(f'   Water voltage std:    {df["water_voltage"].std():.4f} V')
print(f'   Coefficient of Variation: {(df["water_voltage"].std() / df["water_voltage"].mean() * 100):.2f}%')

print('\n🔍 A2 VOLTAGE STABILITY ANALYSIS:')
print(f'   A2 varies by: {(df["air_voltage"].std() / df["air_voltage"].mean() * 100):.2f}% of its mean')
print(f'   Water varies by: {(df["water_voltage"].std() / df["water_voltage"].mean() * 100):.2f}% of its mean')
print(f'   → A2 is {(df["water_voltage"].std() / df["air_voltage"].std()):.1f}x MORE STABLE than water sensor')

# Check if voltage is essentially constant
voltage_changes = df['air_voltage'].diff().abs()
print(f'\n⚡ VOLTAGE CHANGE ANALYSIS:')
print(f'   Average voltage change per minute: {voltage_changes.mean():.5f} V')
print(f'   Max voltage change per minute: {voltage_changes.max():.5f} V')
print(f'   95th percentile change: {voltage_changes.quantile(0.95):.5f} V')

# Find periods where voltage is essentially flat
flat_periods = (voltage_changes < 0.001).sum()
print(f'\n📏 PERIODS WITH ALMOST NO CHANGE (<0.001V):')
print(f'   {flat_periods} out of {len(df)} samples ({flat_periods/len(df)*100:.1f}%)')

# Calculate what resistance would be at different actual temperatures
V_SUPPLY = 3.3
R_BIAS = 100.0

print('\n🧮 WHAT RESISTANCE WOULD WE EXPECT AT DIFFERENT TEMPERATURES?')
print('   (Assuming Pt100 RTD with 100Ω @ 32°F, 0.385Ω/°C = 0.214Ω/°F)')
print('\n   Temp | Expected R | Expected Voltage')
print('   ' + '-'*40)

for temp_f in [55, 60, 65, 70, 75]:
    # Pt100: R = 100 + 0.214*(T - 32)
    expected_r = 100.0 + 0.214 * (temp_f - 32)
    # Voltage divider: V = V_SUPPLY * R_RTD / (R_RTD + R_BIAS)
    expected_v = V_SUPPLY * expected_r / (expected_r + R_BIAS)
    print(f'   {temp_f}°F | {expected_r:6.2f} Ω   | {expected_v:.4f} V')

print('\n📊 WHAT WE ACTUALLY SEE:')
print(f'   Actual average voltage: {df["air_voltage"].mean():.4f} V')
print(f'   Calculated resistance:  {df["air_resistance_ohms"].mean():.2f} Ω')

# What if it's not temperature?
print('\n💡 ALTERNATIVE HYPOTHESIS:')
print('   If A2 voltage stays at ~1.53V regardless of water temp...')
print('   Options:')
print('   1. Fixed resistor (~87Ω) not a sensor')
print('   2. Sensor in wrong location (not in tower air)')
print('   3. Sensor measuring something stable (electronics temperature?)')
print('   4. Wrong sensor type (not RTD)')

# Check correlation between A2 voltage changes and water temp changes
df['water_temp_change'] = df['water_temp_f'].diff()
df['air_voltage_change'] = df['air_voltage'].diff()

corr_changes = df['water_temp_change'].corr(df['air_voltage_change'])
print(f'\n🔗 CORRELATION BETWEEN CHANGES:')
print(f'   Water temp change vs A2 voltage change: {corr_changes:.4f}')
print(f'   → {abs(corr_changes):.4f} correlation means almost NO RELATIONSHIP')

print('\n' + '='*80)
print('CONCLUSION: A2 appears to be measuring something STABLE,')
print('not the air temperature inside the cooling tower.')
print('='*80)
