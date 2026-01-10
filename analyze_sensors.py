import pandas as pd
import numpy as np

# Load data
df = pd.read_csv('sensor_data.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)

print('='*80)
print('COOLING TOWER SENSOR ANALYSIS - 20 HOUR SUMMARY')
print('='*80)
print(f'\n📅 Recording Period:')
print(f'   Start: {df.index.min()}')
print(f'   End:   {df.index.max()}')
print(f'   Duration: {df.index.max() - df.index.min()}')
print(f'   Total samples: {len(df)}')

print(f'\n📊 PRESSURE (A1 - 0-100 psi sensor):')
print(f'   Average:  {df["pressure_psi"].mean():.2f} psi')
print(f'   Min:      {df["pressure_psi"].min():.2f} psi')
print(f'   Max:      {df["pressure_psi"].max():.2f} psi')
print(f'   Range:    {df["pressure_psi"].max() - df["pressure_psi"].min():.2f} psi')
print(f'   Std Dev:  {df["pressure_psi"].std():.2f} psi')

print(f'\n🌡️  WATER TEMPERATURE (A0 - NTC thermistor):')
print(f'   Average:  {df["water_temp_f"].mean():.2f} °F')
print(f'   Min:      {df["water_temp_f"].min():.2f} °F')
print(f'   Max:      {df["water_temp_f"].max():.2f} °F')
print(f'   Range:    {df["water_temp_f"].max() - df["water_temp_f"].min():.2f} °F')
print(f'   Std Dev:  {df["water_temp_f"].std():.2f} °F')

print(f'\n🌡️  AIR TEMPERATURE (A2 - RTD sensor):')
print(f'   Average:  {df["air_temp_f"].mean():.2f} °F')
print(f'   Min:      {df["air_temp_f"].min():.2f} °F')
print(f'   Max:      {df["air_temp_f"].max():.2f} °F')
print(f'   Range:    {df["air_temp_f"].max() - df["air_temp_f"].min():.2f} °F')
print(f'   Std Dev:  {df["air_temp_f"].std():.2f} °F')

print(f'\n⚡ RTD RESISTANCE (A2):')
print(f'   Average:  {df["air_resistance_ohms"].mean():.2f} Ω')
print(f'   Min:      {df["air_resistance_ohms"].min():.2f} Ω')
print(f'   Max:      {df["air_resistance_ohms"].max():.2f} Ω')
print(f'   Range:    {df["air_resistance_ohms"].max() - df["air_resistance_ohms"].min():.2f} Ω')
print(f'   Std Dev:  {df["air_resistance_ohms"].std():.2f} Ω')

print(f'\n🔗 CORRELATIONS:')
corr = df[['pressure_psi', 'water_temp_f', 'air_temp_f']].corr()
print(f'   Water ↔ Air Temp:    {corr.loc["water_temp_f", "air_temp_f"]:.3f}')
print(f'   Pressure ↔ Water:    {corr.loc["pressure_psi", "water_temp_f"]:.3f}')
print(f'   Pressure ↔ Air:      {corr.loc["pressure_psi", "air_temp_f"]:.3f}')

# RTD Calibration
z = np.polyfit(df['air_temp_f'], df['air_resistance_ohms'], 1)
print(f'\n🔬 RTD CALIBRATION ANALYSIS:')
print(f'   Linear fit: R = {z[0]:.4f}T + {z[1]:.2f}')
print(f'   Expected Pt100: 0.214 Ω/°F (0.385 Ω/°C)')
print(f'   Measured slope: {z[0]:.4f} Ω/°F')
print(f'   Difference: {abs(z[0] - 0.214):.4f} Ω/°F ({abs((z[0] - 0.214)/0.214*100):.1f}% deviation)')

# Additional insights
print(f'\n💡 KEY INSIGHTS:')
temp_diff = df["water_temp_f"].mean() - df["air_temp_f"].mean()
print(f'   Average temp difference (water - air): {temp_diff:.2f} °F')
if temp_diff > 5:
    print(f'   → Tower is COOLING water effectively')
elif temp_diff < -5:
    print(f'   → Tower air is WARMER than water (unusual)')
else:
    print(f'   → Temperatures are closely matched')

# Voltage stability
print(f'\n📡 RAW VOLTAGE STABILITY:')
print(f'   Pressure sensor: {df["pressure_voltage"].mean():.4f}V ± {df["pressure_voltage"].std():.4f}V')
print(f'   Water sensor:    {df["water_voltage"].mean():.4f}V ± {df["water_voltage"].std():.4f}V')
print(f'   Air sensor:      {df["air_voltage"].mean():.4f}V ± {df["air_voltage"].std():.4f}V')

print('\n' + '='*80)
