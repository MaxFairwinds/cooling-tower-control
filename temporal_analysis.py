import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from datetime import datetime

# Load data
df = pd.read_csv('sensor_data.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
df.set_index('timestamp', inplace=True)

print('='*80)
print('COOLING TOWER TEMPORAL ANALYSIS - TIME-BASED PATTERNS')
print('='*80)

# Extract hour of day
df['hour'] = df.index.hour

# Hourly averages
hourly = df.groupby('hour').agg({
    'water_temp_f': 'mean',
    'air_temp_f': 'mean',
    'pressure_psi': 'mean'
})

print('\n📊 HOURLY TEMPERATURE AVERAGES:')
print('Hour | Water Temp | Air Temp | Difference')
print('-' * 50)
for hour in sorted(hourly.index):
    water = hourly.loc[hour, 'water_temp_f']
    air = hourly.loc[hour, 'air_temp_f']
    diff = water - air
    print(f'{hour:4d} | {water:10.2f} | {air:8.2f} | {diff:10.2f}')

# Find overnight period (midnight to 6 AM)
overnight = df[(df['hour'] >= 0) & (df['hour'] < 6)]
daytime = df[(df['hour'] >= 12) & (df['hour'] < 18)]

print('\n🌙 OVERNIGHT (12 AM - 6 AM) vs ☀️ DAYTIME (12 PM - 6 PM):')
print(f'Overnight Water Temp: {overnight["water_temp_f"].mean():.2f}°F (min: {overnight["water_temp_f"].min():.2f}°F)')
print(f'Overnight Air Temp:   {overnight["air_temp_f"].mean():.2f}°F (min: {overnight["air_temp_f"].min():.2f}°F)')
print(f'Daytime Water Temp:   {daytime["water_temp_f"].mean():.2f}°F (max: {daytime["water_temp_f"].max():.2f}°F)')
print(f'Daytime Air Temp:     {daytime["air_temp_f"].mean():.2f}°F (max: {daytime["air_temp_f"].max():.2f}°F)')

print(f'\n📉 OVERNIGHT COOLING:')
print(f'Water temp drop: {daytime["water_temp_f"].mean() - overnight["water_temp_f"].mean():.2f}°F')
print(f'Air temp drop:   {daytime["air_temp_f"].mean() - overnight["air_temp_f"].mean():.2f}°F')

# Resample to 15-minute intervals for smoother trend
df_15min = df.resample('15min').mean()

# Calculate rolling correlation over 4-hour windows
df['rolling_corr'] = df['water_temp_f'].rolling(window=240).corr(df['air_temp_f'])

print(f'\n🔗 TIME-BASED CORRELATION ANALYSIS:')
print(f'Overall correlation: {df["water_temp_f"].corr(df["air_temp_f"]):.3f}')
print(f'Average rolling 4-hour correlation: {df["rolling_corr"].mean():.3f}')
print(f'Max correlation period: {df["rolling_corr"].max():.3f}')
print(f'Min correlation period: {df["rolling_corr"].min():.3f}')

# Look at specific time ranges
print('\n📅 TIME PERIOD BREAKDOWN:')
for i in range(0, len(df), 240):  # Every 4 hours
    chunk = df.iloc[i:i+240]
    if len(chunk) > 50:
        start_time = chunk.index[0].strftime('%I:%M %p')
        corr = chunk['water_temp_f'].corr(chunk['air_temp_f'])
        water_change = chunk['water_temp_f'].max() - chunk['water_temp_f'].min()
        air_change = chunk['air_temp_f'].max() - chunk['air_temp_f'].min()
        print(f'{start_time:>8s}: Correlation={corr:6.3f} | Water Δ={water_change:5.2f}°F | Air Δ={air_change:5.2f}°F')

# Create visualizations
fig, axes = plt.subplots(3, 1, figsize=(16, 12))

# Plot 1: Temperature trends over time
axes[0].plot(df.index, df['water_temp_f'], label='Water Temp', color='blue', linewidth=1, alpha=0.7)
axes[0].plot(df.index, df['air_temp_f'], label='Air Temp', color='red', linewidth=1, alpha=0.7)
axes[0].set_ylabel('Temperature (°F)', fontweight='bold')
axes[0].set_title('Water vs Air Temperature Over 23 Hours', fontweight='bold', fontsize=14)
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Plot 2: Temperature difference
df['temp_diff'] = df['water_temp_f'] - df['air_temp_f']
axes[1].plot(df.index, df['temp_diff'], color='green', linewidth=1)
axes[1].axhline(y=0, color='black', linestyle='--', linewidth=1)
axes[1].set_ylabel('Water - Air (°F)', fontweight='bold')
axes[1].set_title('Temperature Difference (Positive = Water Warmer)', fontweight='bold', fontsize=14)
axes[1].grid(True, alpha=0.3)

# Plot 3: Hourly averages
hours = sorted(hourly.index)
axes[2].plot(hours, hourly['water_temp_f'], marker='o', label='Water Temp', color='blue', linewidth=2)
axes[2].plot(hours, hourly['air_temp_f'], marker='s', label='Air Temp', color='red', linewidth=2)
axes[2].set_xlabel('Hour of Day', fontweight='bold')
axes[2].set_ylabel('Temperature (°F)', fontweight='bold')
axes[2].set_title('Average Temperature by Hour of Day', fontweight='bold', fontsize=14)
axes[2].set_xticks(range(0, 24))
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('temperature_analysis.png', dpi=150, bbox_inches='tight')
print('\n📊 Plot saved as: temperature_analysis.png')

# Statistical test for lagged correlation
print('\n⏱️  LAGGED CORRELATION (Does air temp follow water temp?):')
for lag in [1, 5, 10, 30, 60]:  # 1, 5, 10, 30, 60 minute lags
    if lag < len(df):
        lagged_corr = df['water_temp_f'].corr(df['air_temp_f'].shift(lag))
        print(f'   {lag:3d} min lag: {lagged_corr:6.3f}')

print('\n' + '='*80)
