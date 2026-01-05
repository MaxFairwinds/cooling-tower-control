#!/usr/bin/env python3
"""
Simple test script to verify backend structure without hardware
Run on development machine to check imports and basic functionality
"""

import sys
import os

print("="*60)
print("Testing Backend Imports (No Hardware Required)")
print("="*60)

# Test 1: Check if all files exist
files_to_check = [
    'main.py',
    'fan_controller.py',
    'weather_service.py',
    'calculations.py',
    'requirements.txt',
    'Caddyfile',
    'install.sh',
    'README.md'
]

print("\n1. Checking files...")
for f in files_to_check:
    exists = os.path.exists(f)
    status = "✅" if exists else "❌"
    print(f"   {status} {f}")

# Test 2: Try importing modules (will fail on hardware)
print("\n2. Testing imports...")

try:
    from calculations import CalculationService
    print("   ✅ calculations.py")
    
    # Test calculation service
    calc = CalculationService()
    result = calc.calculate(
        basin_temp=75.0,
        pump_hz=45.0,
        outdoor_temp=50.0,
        humidity=60.0
    )
    print(f"   ✅ Heat load calculation: {result['heat_load_kw']:.1f} kW")
    print(f"   ✅ Flow rate: {result['gpm']:.1f} GPM")
    print(f"   ✅ Wet bulb: {result['wet_bulb_f']:.1f}°F")
    
except Exception as e:
    print(f"   ❌ calculations.py: {e}")

try:
    # Weather service (will work without hardware)
    from weather_service import WeatherService
    print("   ✅ weather_service.py")
    
    weather = WeatherService(zip_code="98664")
    print(f"   ✅ Weather service initialized (Vancouver, WA)")
    
except Exception as e:
    print(f"   ❌ weather_service.py: {e}")

# Test 3: Check if FastAPI imports work
print("\n3. Checking FastAPI dependencies...")

try:
    import fastapi
    print(f"   ✅ FastAPI {fastapi.__version__}")
except ImportError:
    print("   ❌ FastAPI not installed (pip install fastapi)")

try:
    import uvicorn
    print(f"   ✅ Uvicorn")
except ImportError:
    print("   ❌ Uvicorn not installed (pip install uvicorn)")

try:
    import pydantic
    print(f"   ✅ Pydantic {pydantic.__version__}")
except ImportError:
    print("   ❌ Pydantic not installed")

try:
    import requests
    print(f"   ✅ Requests {requests.__version__}")
except ImportError:
    print("   ❌ Requests not installed")

print("\n" + "="*60)
print("Test complete!")
print("="*60)
print("\nNext steps:")
print("1. Install dependencies: pip install -r requirements.txt")
print("2. Copy to Raspberry Pi: scp -r backend/* pi@raspberrypi:/home/pi/backend/")
print("3. Run install script on Pi: sudo ./install.sh")
print("4. Test API: http://your-pi:8000/docs")
