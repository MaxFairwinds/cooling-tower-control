#!/usr/bin/env python3
"""
FastAPI Backend for Cooling Tower SCADA System
Real-time WebSocket + REST API for VFD control and monitoring
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import existing hardware modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vfd_controller import MultiVFDManager
from sensor_manager import SensorManager
from pump_failover import PumpFailoverManager
from config import *

# Import new backend services
from fan_controller import FanController
from weather_service import WeatherService
from calculations import CalculationService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global state
class SystemState:
    """Global system state container"""
    def __init__(self):
        self.vfd_manager: Optional[MultiVFDManager] = None
        self.sensors: Optional[SensorManager] = None
        self.pump_manager: Optional[PumpFailoverManager] = None
        self.fan_controller: Optional[FanController] = None
        self.weather_service: Optional[WeatherService] = None
        self.calc_service: Optional[CalculationService] = None
        self.running = False
        self.active_websockets = set()

state = SystemState()

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("="*60)
    logger.info("Starting Cooling Tower SCADA Backend (FastAPI)")
    logger.info("="*60)
    
    try:
        # Initialize hardware
        state.vfd_manager = MultiVFDManager(
            port=SERIAL_PORT,
            baudrate=SERIAL_BAUDRATE,
            parity=SERIAL_PARITY,
            stopbits=SERIAL_STOPBITS,
            bytesize=SERIAL_BYTESIZE
        )
        
        # Add VFDs
        for name, cfg in VFD_CONFIG.items():
            state.vfd_manager.add_vfd(name, cfg['device_id'], cfg['description'])
        
        # Connect to Modbus
        if not state.vfd_manager.connect():
            raise RuntimeError("Failed to connect to Modbus")
        
        # Initialize sensors
        state.sensors = SensorManager(
            i2c_address=SENSOR_CONFIG['i2c_address'],
            gain=SENSOR_CONFIG['ads_gain']
        )
        
        # Initialize pump manager
        pump_primary = state.vfd_manager.get_vfd('pump_primary')
        pump_backup = state.vfd_manager.get_vfd('pump_backup')
        state.pump_manager = PumpFailoverManager(
            pump_primary,
            pump_backup,
            max_errors=PUMP_FAILOVER['max_consecutive_errors'],
            check_interval=PUMP_FAILOVER['health_check_interval']
        )
        
        # Initialize fan controller (NEW)
        fan_vfd = state.vfd_manager.get_vfd('fan')
        state.fan_controller = FanController(
            vfd=fan_vfd,
            target_temp=75.0,
            hysteresis=5.0,
            min_hz=20.0,
            max_hz=60.0
        )
        
        # Initialize weather service (NEW)
        state.weather_service = WeatherService(zip_code="98664")
        
        # Initialize calculation service (NEW)
        state.calc_service = CalculationService()
        
        # Start background tasks
        state.running = True
        asyncio.create_task(sensor_update_loop())
        asyncio.create_task(vfd_update_loop())
        asyncio.create_task(weather_update_loop())
        asyncio.create_task(control_loop())
        
        logger.info("System initialized successfully")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    state.running = False
    
    # Stop all VFDs
    if state.pump_manager:
        state.pump_manager.stop()
    if state.fan_controller:
        state.fan_controller.stop()
    
    # Close Modbus connection
    if state.vfd_manager:
        state.vfd_manager.close()
    
    logger.info("Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Cooling Tower SCADA API",
    description="Real-time monitoring and control for cooling tower system",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware for React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== BACKGROUND TASKS ====================

async def sensor_update_loop():
    """Fast sensor reading loop (1Hz)"""
    while state.running:
        try:
            # This is sync I/O, run in executor to avoid blocking
            await asyncio.sleep(1.0)
            # Sensors are read on-demand in get_sensor_data()
        except Exception as e:
            logger.error(f"Sensor update error: {e}")
            await asyncio.sleep(5.0)

async def vfd_update_loop():
    """Slow VFD status updates (0.1Hz = every 10s)"""
    while state.running:
        try:
            await asyncio.sleep(10.0)
            # VFD status is read on-demand to avoid blocking
        except Exception as e:
            logger.error(f"VFD update error: {e}")
            await asyncio.sleep(30.0)

async def weather_update_loop():
    """Weather data refresh (every 15 min)"""
    while state.running:
        try:
            await state.weather_service.update()
            logger.info(f"Weather updated: {state.weather_service.get_data()}")
            await asyncio.sleep(900)  # 15 minutes
        except Exception as e:
            logger.error(f"Weather update error: {e}")
            await asyncio.sleep(300)  # Retry in 5 min

async def control_loop():
    """Main control loop (1Hz)"""
    while state.running:
        try:
            # Read sensors (blocking, but fast ~0.02s)
            sensor_data = await asyncio.get_event_loop().run_in_executor(
                None, state.sensors.read_all
            )
            basin_temp = sensor_data.get('temperature_f', 0.0)
            pressure = sensor_data.get('pressure_psi', 0.0)
            
            # Update fan controller
            if state.fan_controller.auto_mode:
                state.fan_controller.update(basin_temp)
            
            # Update pump controller (pressure-based)
            if state.pump_manager:
                error = CONTROL_PARAMS['target_pressure'] - pressure
                output_hz = 30.0 + (error * CONTROL_PARAMS['kp'])
                output_hz = max(
                    CONTROL_PARAMS['min_frequency'],
                    min(CONTROL_PARAMS['max_frequency'], output_hz)
                )
                # Only update if in auto mode
                # For now, keep manual (as per user requirement)
                # state.pump_manager.set_frequency(output_hz)
            
            # Check pump health
            if PUMP_FAILOVER['auto_failover_enabled']:
                await asyncio.get_event_loop().run_in_executor(
                    None, state.pump_manager.check_health
                )
            
            await asyncio.sleep(1.0)
            
        except Exception as e:
            logger.error(f"Control loop error: {e}")
            await asyncio.sleep(5.0)

# ==================== PYDANTIC MODELS ====================

class SensorData(BaseModel):
    pressure_psi: float
    basin_temp_f: float
    timestamp: str
    status: str  # "online" | "offline"

class VFDStatus(BaseModel):
    state: str  # "Running" | "Stopped" | "Fault" | "NoComm"
    frequency: float
    current: float
    fault_code: int

class WeatherData(BaseModel):
    outdoor_temp_f: float
    humidity_pct: float
    wet_bulb_f: float
    last_update: str
    status: str  # "online" | "stale" | "offline"

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
    active_pump: str  # "primary" | "backup"
    weather: WeatherData
    calculated: CalculatedData
    fan_auto_mode: bool
    fan_setpoint: float

class FanModeRequest(BaseModel):
    mode: str  # "manual" | "auto"

class FanSetpointRequest(BaseModel):
    hz: float

class FanAutoConfigRequest(BaseModel):
    target_temp: float
    hysteresis: float

# ==================== HELPER FUNCTIONS ====================

def get_sensor_data() -> SensorData:
    """Read sensor data (blocking I/O)"""
    try:
        data = state.sensors.read_all()
        return SensorData(
            pressure_psi=data.get('pressure_psi', 0.0),
            basin_temp_f=data.get('temperature_f', 0.0),
            timestamp=datetime.now().isoformat(),
            status="online"
        )
    except Exception as e:
        logger.error(f"Sensor read error: {e}")
        return SensorData(
            pressure_psi=0.0,
            basin_temp_f=0.0,
            timestamp=datetime.now().isoformat(),
            status="offline"
        )

def get_vfd_status(vfd) -> VFDStatus:
    """Read VFD status (blocking I/O)"""
    try:
        status = vfd.get_status()
        # Map state names to match UI expectations
        state_map = {
            "Forward": "Running",
            "Stopped": "Stopped",
            "Fault": "Fault",
            "NoComm": "NoComm"
        }
        return VFDStatus(
            state=state_map.get(status.get('state', 'NoComm'), 'NoComm'),
            frequency=status.get('output_frequency', 0.0),
            current=status.get('output_current', 0.0),
            fault_code=status.get('fault_code', 0)
        )
    except Exception as e:
        logger.error(f"VFD read error: {e}")
        return VFDStatus(state="NoComm", frequency=0.0, current=0.0, fault_code=0)

async def get_full_system_status() -> SystemStatus:
    """Get complete system status (combines all data sources)"""
    # Run blocking I/O in executor
    loop = asyncio.get_event_loop()
    
    sensors = await loop.run_in_executor(None, get_sensor_data)
    fan = await loop.run_in_executor(
        None, get_vfd_status, state.vfd_manager.get_vfd('fan')
    )
    pump_primary = await loop.run_in_executor(
        None, get_vfd_status, state.vfd_manager.get_vfd('pump_primary')
    )
    pump_backup = await loop.run_in_executor(
        None, get_vfd_status, state.vfd_manager.get_vfd('pump_backup')
    )
    
    # Get weather data
    weather_data = state.weather_service.get_data()
    weather = WeatherData(
        outdoor_temp_f=weather_data.get('temp_f', 0.0),
        humidity_pct=weather_data.get('humidity', 0.0),
        wet_bulb_f=weather_data.get('wet_bulb_f', 0.0),
        last_update=weather_data.get('last_update', ''),
        status=weather_data.get('status', 'offline')
    )
    
    # Calculate derived values
    pump_hz = max(pump_primary.frequency, pump_backup.frequency)
    calc_data = state.calc_service.calculate(
        basin_temp=sensors.basin_temp_f,
        pump_hz=pump_hz,
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
        fan=fan,
        pump_primary=pump_primary,
        pump_backup=pump_backup,
        active_pump=state.pump_manager.get_status()['active_pump'],
        weather=weather,
        calculated=calculated,
        fan_auto_mode=state.fan_controller.auto_mode,
        fan_setpoint=state.fan_controller.manual_setpoint
    )

# ==================== WEBSOCKET ====================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time system updates"""
    await websocket.accept()
    state.active_websockets.add(websocket)
    logger.info(f"WebSocket client connected. Total: {len(state.active_websockets)}")
    
    try:
        while True:
            # Send full system status every 500ms
            status = await get_full_system_status()
            await websocket.send_json(status.dict())
            await asyncio.sleep(0.5)
            
    except WebSocketDisconnect:
        state.active_websockets.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(state.active_websockets)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        state.active_websockets.discard(websocket)

# ==================== REST API ENDPOINTS ====================

@app.get("/api/status")
async def get_status():
    """Get complete system status (legacy compatibility)"""
    return await get_full_system_status()

@app.get("/api/sensors")
async def get_sensors():
    """Get sensor data only (fast endpoint)"""
    return await asyncio.get_event_loop().run_in_executor(None, get_sensor_data)

@app.get("/api/vfds")
async def get_vfds():
    """Get VFD status (slow endpoint)"""
    loop = asyncio.get_event_loop()
    fan, pump1, pump2 = await asyncio.gather(
        loop.run_in_executor(None, get_vfd_status, state.vfd_manager.get_vfd('fan')),
        loop.run_in_executor(None, get_vfd_status, state.vfd_manager.get_vfd('pump_primary')),
        loop.run_in_executor(None, get_vfd_status, state.vfd_manager.get_vfd('pump_backup'))
    )
    return {
        "fan": fan,
        "pump_primary": pump1,
        "pump_backup": pump2,
        "active_pump": state.pump_manager.get_status()['active_pump']
    }

@app.get("/api/weather")
async def get_weather():
    """Get weather data"""
    data = state.weather_service.get_data()
    return WeatherData(
        outdoor_temp_f=data.get('temp_f', 0.0),
        humidity_pct=data.get('humidity', 0.0),
        wet_bulb_f=data.get('wet_bulb_f', 0.0),
        last_update=data.get('last_update', ''),
        status=data.get('status', 'offline')
    )

@app.post("/api/fan/mode")
async def set_fan_mode(request: FanModeRequest):
    """Set fan control mode (manual/auto)"""
    if request.mode == "auto":
        state.fan_controller.enable_auto()
    elif request.mode == "manual":
        state.fan_controller.enable_manual()
    else:
        raise HTTPException(status_code=400, detail="Invalid mode")
    
    return {"success": True, "mode": request.mode}

@app.post("/api/fan/setpoint")
async def set_fan_setpoint(request: FanSetpointRequest):
    """Set fan frequency (manual mode only)"""
    if state.fan_controller.auto_mode:
        raise HTTPException(status_code=400, detail="Cannot set frequency in auto mode")
    
    await asyncio.get_event_loop().run_in_executor(
        None, state.fan_controller.set_manual_frequency, request.hz
    )
    return {"success": True, "hz": request.hz}

@app.post("/api/fan/auto_config")
async def set_fan_auto_config(request: FanAutoConfigRequest):
    """Configure fan auto mode parameters"""
    state.fan_controller.target_temp = request.target_temp
    state.fan_controller.hysteresis = request.hysteresis
    return {"success": True, "config": request.dict()}

@app.post("/api/pump/frequency")
async def set_pump_frequency(hz: float):
    """Set pump frequency (manual control)"""
    await asyncio.get_event_loop().run_in_executor(
        None, state.pump_manager.set_frequency, hz
    )
    return {"success": True, "hz": hz}

@app.post("/api/pump/start")
async def start_pump():
    """Start active pump"""
    pump = state.pump_manager.get_active_vfd()
    await asyncio.get_event_loop().run_in_executor(None, pump.start)
    return {"success": True}

@app.post("/api/pump/stop")
async def stop_pump():
    """Stop active pump"""
    await asyncio.get_event_loop().run_in_executor(None, state.pump_manager.stop)
    return {"success": True}

@app.post("/api/pump/switch")
async def switch_pump():
    """Switch active pump"""
    current = state.pump_manager.get_status()['active_pump']
    if current == 'primary':
        await asyncio.get_event_loop().run_in_executor(
            None, state.pump_manager._failover_to_backup
        )
    else:
        await asyncio.get_event_loop().run_in_executor(
            None, state.pump_manager._failback_to_primary
        )
    return {"success": True}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "websocket_clients": len(state.active_websockets),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
