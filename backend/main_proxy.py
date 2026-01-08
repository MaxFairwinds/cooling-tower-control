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
from pydantic import BaseModel

# Import weather service
from weather_service import WeatherService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask dashboard URL and credentials
FLASK_URL = "http://localhost:8001"
FLASK_USERNAME = "admin"
FLASK_PASSWORD = "cooling2025"

# Global state
class SystemState:
    """Global system state container"""
    def __init__(self):
        self.running = False
        self.active_websockets = set()
        self.http_client: Optional[httpx.AsyncClient] = None
        self.weather_service: Optional[WeatherService] = None
        self.latest_data = {}
        self.last_update = None

state = SystemState()

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("="*60)
    logger.info("Starting Cooling Tower SCADA Backend (PROXY MODE)")
    logger.info(f"Flask Dashboard: {FLASK_URL}")
    logger.info("="*60)
    
    # Create HTTP client with cookie jar
    state.http_client = httpx.AsyncClient(
        timeout=5.0,
        follow_redirects=False,  # Manual redirect handling
        cookies=httpx.Cookies()  # Enable cookie jar
    )
    
    # Login to Flask to get session cookie
    try:
        login_response = await state.http_client.post(
            f"{FLASK_URL}/login",
            data={"username": FLASK_USERNAME, "password": FLASK_PASSWORD},
            follow_redirects=False
        )
        
        if login_response.status_code in [302, 200]:
            # Check if we got a session cookie
            if state.http_client.cookies:
                logger.info(f"✓ Logged in to Flask dashboard (cookies: {len(state.http_client.cookies)})")
            else:
                logger.warning("Login redirect but no cookies received")
        else:
            logger.warning(f"Flask login returned {login_response.status_code}")
    except Exception as e:
        logger.error(f"Flask login failed: {e}")
    
    # Test connection to Flask
    try:
        response = await state.http_client.get(f"{FLASK_URL}/api/status")
        if response.status_code == 200:
            logger.info("✓ Connected to Flask dashboard successfully")
            state.latest_data = response.json()
        elif response.status_code == 401:
            logger.warning("Flask requires authentication - will need to handle login")
        else:
            logger.warning(f"Flask returned status {response.status_code}")
    except Exception as e:
        logger.error(f"Could not connect to Flask: {e}")
        logger.error("Make sure Flask dashboard is running on port 8001")
    
    # Initialize weather service
    state.weather_service = WeatherService(zip_code="98664")
    await state.weather_service.update()
    logger.info("✓ Weather service initialized")
    
    # Start background tasks
    state.running = True
    asyncio.create_task(flask_poll_loop())
    asyncio.create_task(weather_update_loop())
    
    logger.info("Backend started in PROXY mode")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    state.running = False
    
    if state.http_client:
        await state.http_client.aclose()
    
    logger.info("Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Cooling Tower SCADA API (Proxy)",
    description="Real-time monitoring and control - proxies Flask dashboard",
    version="2.0.0-proxy",
    lifespan=lifespan
)

# CORS middleware for React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== BACKGROUND TASKS ====================

async def flask_poll_loop():
    """Poll Flask API for updates"""
    while state.running:
        try:
            response = await state.http_client.get(f"{FLASK_URL}/api/status")
            if response.status_code == 200:
                state.latest_data = response.json()
                state.last_update = datetime.now()
                
                # Broadcast to all WebSocket clients
                if state.active_websockets:
                    transformed = transform_flask_data(state.latest_data)
                    for ws in list(state.active_websockets):
                        try:
                            await ws.send_json(transformed)
                        except:
                            state.active_websockets.discard(ws)
            else:
                logger.warning(f"Flask returned status {response.status_code}")
            
            await asyncio.sleep(0.5)  # Poll every 500ms
            
        except Exception as e:
            logger.error(f"Flask poll error: {e}")
            await asyncio.sleep(2.0)

async def weather_update_loop():
    """Update weather data every 15 minutes"""
    while state.running:
        try:
            await state.weather_service.update()
            logger.info(f"Weather updated: {state.weather_service.get_data()}")
            await asyncio.sleep(900)  # 15 minutes
        except Exception as e:
            logger.error(f"Weather update error: {e}")
            await asyncio.sleep(300)  # Retry in 5 min

# ==================== DATA TRANSFORMATION ====================

def transform_flask_data(flask_data: dict) -> dict:
    """Transform Flask API response to match new frontend expectations"""
    
    # Flask format:
    # {
    #   "sensors": {"pressure_psi": 12.5, "temperature_f": 72.0},
    #   "fan": {"state": "Running", "frequency": 45.0, "current": 12.3, "fault": 0},
    #   "pump_primary": {...},
    #   "pump_backup": {...},
    #   "active_pump": "primary",
    #   "timestamp": "2026-01-06T..."
    # }
    
    # Get real weather data
    weather_data = state.weather_service.get_data() if state.weather_service else {}
    
    # Map Flask VFD states to frontend-expected states
    def map_state(flask_state: str) -> str:
        """Map Flask VFD states to frontend expectations"""
        mapping = {
            "Forward": "Running",
            "Reverse": "Running",
            "Stopped": "Stopped",
            "Fault": "Fault",
            "Unknown": "NoComm"
        }
        return mapping.get(flask_state, flask_state)
    
    sensors = flask_data.get('sensors', {})
    fan = flask_data.get('fan', {})
    pump_primary = flask_data.get('pump_primary', {})
    pump_backup = flask_data.get('pump_backup', {})
    
    return {
        "sensors": {
            "pressure_psi": sensors.get('pressure_psi', 0.0),
            "basin_temp_f": sensors.get('temperature_f', 0.0),
            "timestamp": flask_data.get('timestamp', datetime.now().isoformat()),
            "status": "online"
        },
        "fan": {weather_data.get('temp_f', 0.0),
            "humidity_pct": weather_data.get('humidity', 0.0),
            "wet_bulb_f": weather_data.get('wet_bulb_f', 0.0),
            "last_update": weather_data.get('last_update', datetime.now().isoformat()),
            "status": weather_data.get('status', 'offline')et('fault', 0)
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
            "outdoor_temp_f": 65.0,
            "humidity_pct": 50.0,
            "wet_bulb_f": 55.0,
            "last_update": datetime.now().isoformat(),
            "status": "offline"
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

# ==================== WEBSOCKET ====================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time system updates"""
    await websocket.accept()
    state.active_websockets.add(websocket)
    logger.info(f"WebSocket client connected. Total: {len(state.active_websockets)}")
    
    try:
        # Send initial data immediately
        if state.latest_data:
            await websocket.send_json(transform_flask_data(state.latest_data))
        
        # Keep connection alive - just wait for disconnect
        # The poll loop will send updates automatically
        while True:
            # Wait for close event or client ping
            try:
                message = await websocket.receive_text()
                # Client sent something (likely a ping), ignore it
            except Exception:
                # Connection closed or error
                break
                
    except WebSocketDisconnect:
        state.active_websockets.remove(websocket)
        logger.info(f"WebSocket client disconnected. Total: {len(state.active_websockets)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        state.active_websockets.discard(websocket)

# ==================== REST API ENDPOINTS ====================

@app.get("/api/status")
async def get_status():
    """Get complete system status"""
    if not state.latest_data:
        # Try to fetch now
        try:
            response = await state.http_client.get(f"{FLASK_URL}/api/status")
            if response.status_code == 200:
                state.latest_data = response.json()
            else:
                return {"error": "Flask not available", "status_code": response.status_code}
        except Exception as e:
            return {"error": str(e)}
    
    return transform_flask_data(state.latest_data)

@app.get("/api/sensors")
async def get_sensors():
    """Get sensor data only"""
    if state.latest_data:
        return transform_flask_data(state.latest_data)["sensors"]
    return {"status": "offline"}

@app.get("/api/vfds")
async def get_vfds():
    """Get VFD status"""
    if state.latest_data:
        data = transform_flask_data(state.latest_data)
        return {
            "fan": data["fan"],
            "pump_primary": data["pump_primary"],
            "pump_backup": data["pump_backup"],
            "active_pump": data["active_pump"]
        }
    return {}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
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

# READ-ONLY MODE - All control endpoints return 403
@app.post("/api/fan/mode")
async def set_fan_mode():
    return {"error": "Read-only mode - controls disabled"}, 403

@app.post("/api/fan/setpoint")
async def set_fan_setpoint():
    return {"error": "Read-only mode - controls disabled"}, 403

@app.post("/api/pump/frequency")
async def set_pump_frequency():
    return {"error": "Read-only mode - controls disabled"}, 403

@app.post("/api/pump/start")
async def start_pump():
    return {"error": "Read-only mode - controls disabled"}, 403

@app.post("/api/pump/stop")
async def stop_pump():
    return {"error": "Read-only mode - controls disabled"}, 403

@app.post("/api/pump/switch")
async def switch_pump():
    return {"error": "Read-only mode - controls disabled"}, 403

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_proxy:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )
