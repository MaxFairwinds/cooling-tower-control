#!/usr/bin/env python3
"""
Mock Backend for Testing (No Hardware Required)
Simulates sensors and VFDs for development/testing
"""

import asyncio
import random
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import calculation services (no hardware needed)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.calculations import CalculationService
from backend.weather_service import WeatherService

app = FastAPI(title="Cooling Tower SCADA API (Mock)", version="2.0.0-mock")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock state
class MockState:
    def __init__(self):
        self.basin_temp = 75.0
        self.pressure = 45.0
        self.fan_hz = 0.0
        self.fan_running = False
        self.fan_auto = False
        self.pump_hz = 45.0
        self.active_pump = "primary"
        self.calc_service = CalculationService()
        self.weather_service = WeatherService(zip_code="98664")

state = MockState()

# Pydantic models
class SensorData(BaseModel):
    pressure_psi: float
    basin_temp_f: float
    timestamp: str
    status: str

class VFDStatus(BaseModel):
    state: str
    frequency: float
    current: float
    fault_code: int

class WeatherData(BaseModel):
    outdoor_temp_f: float
    humidity_pct: float
    wet_bulb_f: float
    last_update: str
    status: str

class CalculatedData(BaseModel):
    return_temp_f: float
    heat_load_kw: float
    gpm: float
    approach_f: float

class SystemStatus(BaseModel):
    sensors: SensorData
    fan: VFDStatus
    pump_primary: VFDStatus
    pump_backup: VFDStatus
    active_pump: str
    weather: WeatherData
    calculated: CalculatedData
    fan_auto_mode: bool
    fan_setpoint: float

# Mock sensor reading
def get_mock_sensors() -> SensorData:
    # Add some realistic noise
    temp_noise = random.uniform(-0.2, 0.2)
    pressure_noise = random.uniform(-0.5, 0.5)
    
    return SensorData(
        pressure_psi=state.pressure + pressure_noise,
        basin_temp_f=state.basin_temp + temp_noise,
        timestamp=datetime.now().isoformat(),
        status="online"
    )

# Mock VFD status
def get_mock_vfd(name: str, hz: float, running: bool) -> VFDStatus:
    return VFDStatus(
        state="Running" if running and hz > 0 else "Stopped",
        frequency=hz,
        current=(hz / 60.0) * 18.0 if running else 0.0,
        fault_code=0
    )

async def get_full_status() -> SystemStatus:
    sensors = get_mock_sensors()
    
    # Mock weather (will try real API)
    weather_data = state.weather_service.get_data()
    if weather_data['status'] == 'offline':
        # Use defaults if weather not available
        weather_data = {
            'temp_f': 50.0,
            'humidity': 60.0,
            'wet_bulb_f': 38.0,
            'last_update': datetime.now().isoformat(),
            'status': 'mock'
        }
    
    weather = WeatherData(
        outdoor_temp_f=weather_data['temp_f'],
        humidity_pct=weather_data['humidity'],
        wet_bulb_f=weather_data['wet_bulb_f'],
        last_update=weather_data['last_update'],
        status=weather_data['status']
    )
    
    # Calculate derived values
    calc_data = state.calc_service.calculate(
        basin_temp=sensors.basin_temp_f,
        pump_hz=state.pump_hz,
        outdoor_temp=weather.outdoor_temp_f,
        humidity=weather.humidity_pct
    )
    
    calculated = CalculatedData(
        return_temp_f=calc_data['return_temp_f'],
        heat_load_kw=calc_data['heat_load_kw'],
        gpm=calc_data['gpm'],
        approach_f=calc_data['approach_f']
    )
    
    return SystemStatus(
        sensors=sensors,
        fan=get_mock_vfd("fan", state.fan_hz, state.fan_running),
        pump_primary=get_mock_vfd("pump1", state.pump_hz if state.active_pump == "primary" else 0, state.active_pump == "primary"),
        pump_backup=get_mock_vfd("pump2", state.pump_hz if state.active_pump == "backup" else 0, state.active_pump == "backup"),
        active_pump=state.active_pump,
        weather=weather,
        calculated=calculated,
        fan_auto_mode=state.fan_auto,
        fan_setpoint=state.fan_hz
    )

# WebSocket
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ WebSocket client connected")
    
    try:
        while True:
            status = await get_full_status()
            await websocket.send_json(status.dict())
            await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        print("❌ WebSocket client disconnected")

# REST endpoints
@app.get("/api/status")
async def get_status():
    return await get_full_status()

@app.get("/api/sensors")
async def get_sensors():
    return get_mock_sensors()

@app.post("/api/fan/mode")
async def set_fan_mode(mode: str):
    state.fan_auto = (mode == "auto")
    print(f"Fan mode: {mode}")
    return {"success": True, "mode": mode}

@app.post("/api/fan/setpoint")
async def set_fan_setpoint(hz: float):
    state.fan_hz = hz
    state.fan_running = (hz > 0)
    print(f"Fan setpoint: {hz} Hz")
    return {"success": True, "hz": hz}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "mode": "mock", "timestamp": datetime.now().isoformat()}

@app.get("/")
async def root():
    return {
        "message": "Cooling Tower SCADA API (Mock Mode)",
        "docs": "/docs",
        "websocket": "ws://localhost:8000/ws"
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Starting Mock Backend (No Hardware)")
    print("="*60)
    print("API Docs:   http://localhost:8000/docs")
    print("Health:     http://localhost:8000/api/health")
    print("WebSocket:  ws://localhost:8000/ws")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
