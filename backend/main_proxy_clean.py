#!/usr/bin/env python3
"""
FastAPI Backend for Cooling Tower SCADA System - PROXY MODE
Fetches data from Flask dashboard instead of directly accessing VFDs
This eliminates RS-485 Modbus bus conflicts
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager
import httpx

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from weather_service import WeatherService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

FLASK_URL = "http://localhost:8001"
FLASK_USERNAME = "admin"
FLASK_PASSWORD = "cooling2025"

class SystemState:
    def __init__(self):
        self.running = False
        self.active_websockets = set()
        self.http_client: Optional[httpx.AsyncClient] = None
        self.weather_service: Optional[WeatherService] = None
        self.latest_data = {}
        self.last_update = None

state = SystemState()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("="*60)
    logger.info("Starting Cooling Tower SCADA Backend (PROXY MODE)")
    logger.info(f"Flask Dashboard: {FLASK_URL}")
    logger.info("="*60)
    
    state.http_client = httpx.AsyncClient(timeout=5.0, follow_redirects=False, cookies=httpx.Cookies())
    
    try:
        login_response = await state.http_client.post(
            f"{FLASK_URL}/login",
            data={"username": FLASK_USERNAME, "password": FLASK_PASSWORD},
            follow_redirects=False
        )
        if login_response.status_code in [302, 200] and state.http_client.cookies:
            logger.info(f"✓ Logged in to Flask dashboard (cookies: {len(state.http_client.cookies)})")
    except Exception as e:
        logger.error(f"Flask login failed: {e}")
    
    try:
        response = await state.http_client.get(f"{FLASK_URL}/api/status")
        if response.status_code == 200:
            logger.info("✓ Connected to Flask dashboard successfully")
            state.latest_data = response.json()
    except Exception as e:
        logger.error(f"Could not connect to Flask: {e}")
    
    state.weather_service = WeatherService(zip_code="98664")
    await state.weather_service.update()
    logger.info("✓ Weather service initialized")
    
    state.running = True
    asyncio.create_task(flask_poll_loop())
    asyncio.create_task(weather_update_loop())
    logger.info("Backend started in PROXY mode")
    
    yield
    
    logger.info("Shutting down...")
    state.running = False
    if state.http_client:
        await state.http_client.aclose()
    logger.info("Shutdown complete")

app = FastAPI(title="Cooling Tower SCADA API (Proxy)", version="2.0.0-proxy", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

async def flask_poll_loop():
    while state.running:
        try:
            response = await state.http_client.get(f"{FLASK_URL}/api/status")
            if response.status_code == 200:
                state.latest_data = response.json()
                state.last_update = datetime.now()
                if state.active_websockets:
                    transformed = transform_flask_data(state.latest_data)
                    for ws in list(state.active_websockets):
                        try:
                            await ws.send_json(transformed)
                        except:
                            state.active_websockets.discard(ws)
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Flask poll error: {e}")
            await asyncio.sleep(2.0)

async def weather_update_loop():
    while state.running:
        try:
            await state.weather_service.update()
            logger.info(f"Weather updated: {state.weather_service.get_data()}")
            await asyncio.sleep(900)
        except Exception as e:
            logger.error(f"Weather update error: {e}")
            await asyncio.sleep(300)

def transform_flask_data(flask_data: dict) -> dict:
    def map_state(s: str) -> str:
        return {"Forward": "Running", "Reverse": "Running", "Stopped": "Stopped", "Fault": "Fault", "Unknown": "NoComm"}.get(s, s)
    
    sensors = flask_data.get('sensors', {})
    fan = flask_data.get('fan', {})
    pump_primary = flask_data.get('pump_primary', {})
    pump_backup = flask_data.get('pump_backup', {})
    weather_data = state.weather_service.get_data() if state.weather_service else {}
    
    return {
        "sensors": {
            "pressure_psi": sensors.get('pressure_psi', 0.0),
            "basin_temp_f": sensors.get('temperature_f', 0.0),
            "timestamp": flask_data.get('timestamp', datetime.now().isoformat()),
            "status": "online"
        },
        "fan": {
            "state": map_state(fan.get('state', 'Unknown')),
            "frequency": fan.get('frequency', 0.0),
            "current": fan.get('current', 0.0),
            "fault_code": fan.get('fault', 0)
        },
        "pump_primary": {
            "state": map_state(pump_primary.get('state', 'Unknown')),
            "frequency": pump_primary.get('frequency', 0.0),
            "current": pump_primary.get('current', 0.0),
            "fault_code": pump_primary.get('fault', 0)
        },
        "pump_backup": {
            "state": map_state(pump_backup.get('state', 'Unknown')),
            "frequency": pump_backup.get('frequency', 0.0),
            "current": pump_backup.get('current', 0.0),
            "fault_code": pump_backup.get('fault', 0)
        },
        "active_pump": flask_data.get('active_pump', 'primary'),
        "weather": {
            "outdoor_temp_f": weather_data.get('temp_f', 0.0),
            "humidity_pct": weather_data.get('humidity', 0.0),
            "wet_bulb_f": weather_data.get('wet_bulb_f', 0.0),
            "last_update": weather_data.get('last_update', datetime.now().isoformat()),
            "status": weather_data.get('status', 'offline')
        },
        "calculated": {
            "return_temp_f": sensors.get('temperature_f', 0.0) + 10.0,
            "heat_load_kw": 0.0,
            "gpm": 0.0,
            "approach_f": 0.0
        },
        "fan_auto_mode": False,
        "fan_setpoint": fan.get('frequency', 0.0)
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    state.active_websockets.add(websocket)
    logger.info(f"WebSocket client connected. Total: {len(state.active_websockets)}")
    try:
        if state.latest_data:
            await websocket.send_json(transform_flask_data(state.latest_data))
        while True:
            try:
                await websocket.receive_text()
            except Exception:
                break
    except WebSocketDisconnect:
        state.active_websockets.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(state.active_websockets)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        state.active_websockets.discard(websocket)

@app.get("/api/status")
async def get_status():
    if not state.latest_data:
        try:
            response = await state.http_client.get(f"{FLASK_URL}/api/status")
            if response.status_code == 200:
                state.latest_data = response.json()
        except:
            pass
    return transform_flask_data(state.latest_data)

@app.get("/api/health")
async def health_check():
    flask_healthy = False
    try:
        response = await state.http_client.get(f"{FLASK_URL}/api/status", timeout=2.0)
        flask_healthy = response.status_code == 200
    except:
        pass
    return {
        "status": "healthy" if flask_healthy else "degraded",
        "flask_connected": flask_healthy,
        "websocket_clients": len(state.active_websockets),
        "last_update": state.last_update.isoformat() if state.last_update else None,
        "timestamp": datetime.now().isoformat()
    }

# Pump control endpoints - proxy to Flask
@app.post("/api/pump/frequency")
async def set_pump_frequency(request: dict):
    try:
        # Translate 'hz' to 'frequency' for Flask API
        flask_request = {"frequency": request.get("hz", request.get("frequency"))}
        response = await state.http_client.post(
            f"{FLASK_URL}/api/vfd/pump/frequency",
            json=request
        )
        return response.json()
    except Exception as e:
        logger.error(f"Pump frequency control failed: {e}")
        return {"error": str(e)}, 500

@app.post("/api/pump/start")
async def start_pump():
    try:
        response = await state.http_client.post(f"{FLASK_URL}/api/vfd/pump/start")
        return response.json()
    except Exception as e:
        logger.error(f"Pump start failed: {e}")
        return {"error": str(e)}, 500

@app.post("/api/pump/stop")
async def stop_pump():
    try:
        response = await state.http_client.post(f"{FLASK_URL}/api/vfd/pump/stop")
        return response.json()
    except Exception as e:
        logger.error(f"Pump stop failed: {e}")
        return {"error": str(e)}, 500

@app.post("/api/pump/switch")
async def switch_pump():
    try:
        response = await state.http_client.post(f"{FLASK_URL}/api/pump/switch")
        return response.json()
    except Exception as e:
        logger.error(f"Pump switch failed: {e}")
        return {"error": str(e)}, 500

# Fan control endpoints - proxy to Flask
@app.post("/api/fan/mode")
async def set_fan_mode(request: dict):
    try:
        # Flask uses /api/auto to toggle auto mode
        response = await state.http_client.post(
            f"{FLASK_URL}/api/auto",
            json=request
        )
        return response.json()
    except Exception as e:
        logger.error(f"Fan mode control failed: {e}")
        return {"error": str(e)}, 500

@app.post("/api/fan/setpoint")
async def set_fan_setpoint(request: dict):
    try:
        # Translate 'hz' to 'frequency' for Flask API
        flask_request = {"frequency": request.get("hz", request.get("frequency"))}
        response = await state.http_client.post(
            f"{FLASK_URL}/api/vfd/fan/frequency",
            json=flask_request
        )
        return response.json()
    except Exception as e:
        logger.error(f"Fan setpoint control failed: {e}")
        return {"error": str(e)}, 500

@app.post("/api/fan/auto_config")
async def set_fan_auto_config(request: dict):
    try:
        response = await state.http_client.post(
            f"{FLASK_URL}/api/fan/auto_config",
            json=request
        )
        return response.json()
    except Exception as e:
        logger.error(f"Fan auto config failed: {e}")
        return {"error": str(e)}, 500

@app.post("/api/fan/start")
async def start_fan():
    try:
        response = await state.http_client.post(f"{FLASK_URL}/api/vfd/fan/start")
        return response.json()
    except Exception as e:
        logger.error(f"Fan start failed: {e}")
        return {"error": str(e)}, 500

@app.post("/api/fan/stop")
async def stop_fan():
    try:
        response = await state.http_client.post(f"{FLASK_URL}/api/vfd/fan/stop")
        return response.json()
    except Exception as e:
        logger.error(f"Fan stop failed: {e}")
        return {"error": str(e)}, 500
