# UI Integration Status - January 5, 2026

## ✅ Completed Components

### Backend (FastAPI)
- [x] WebSocket endpoint streaming full system status @ 500ms
- [x] REST API for all control actions
- [x] Fan controller with Manual/Auto modes
- [x] Weather.gov API integration
- [x] Heat load calculations
- [x] Pump failover system
- [x] Sensor reading (ADS1115)
- [x] VFD control (Modbus RTU)

### Frontend (React)
- [x] WebSocket hook (`useWebSocket.ts`) 
- [x] API client (`api.ts`)
- [x] Data mapping from backend to UI state
- [x] Control handlers calling API endpoints
- [x] Fan manual/auto mode toggle
- [x] Pump start/stop/switch controls
- [x] Real-time sensor display
- [x] Connection status indicator

## ⚠️ Partial Implementation (Still Using Simulation)

### App.tsx Issues

1. **Pressure Sensor** (Lines ~385-388)
   ```typescript
   // CURRENT: Simulated pressure
   const basePressure = 15 + (activeFreq / 60) * 35; 
   const dischargePressure = basePressure + (Math.random() - 0.5);
   
   // NEEDED: Use real sensor
   const dischargePressure = backendData?.sensors.pressure_psi || 0;
   ```

2. **Delta-T Calculation** (Lines ~380-381)
   ```typescript
   // CURRENT: Hardcoded delta
   const visualDeltaT = (system.isRunning && flowFactor > 0.1) ? 10.0 : 1.0;
   
   // NEEDED: Use calculated return temp
   const visualDeltaT = backendData 
     ? backendData.calculated.return_temp_f - backendData.sensors.basin_temp_f 
     : 0;
   ```

3. **WSHP Discharge Air Temp** (Lines ~418-440)
   ```typescript
   // CURRENT: Local physics simulation
   if (system.temperature <= EFFICIENCY_KNEE) {
       dischargeAirTemp = TARGET_LAT;
   } else {
       const excessHeat = system.temperature - EFFICIENCY_KNEE;
       const penalty = excessHeat * 0.6; 
       dischargeAirTemp = Math.min(TARGET_LAT + penalty, ROOM_TEMP);
   }
   
   // OPTION 1: Keep simulation (it's educational/useful)
   // OPTION 2: Remove if not needed
   // OPTION 3: Add backend calculation and use that
   ```

4. **Wet Bulb Calculation** (Line ~390)
   ```typescript
   // CURRENT: Local approximation
   const currentWetBulb = system.outdoorTemp - ((100 - system.humidity) * 0.3);
   
   // NEEDED: Already calculated by backend!
   const currentWetBulb = backendData?.weather.wet_bulb_f || 0;
   ```

5. **Flow Rate (GPM) Display** (Missing)
   - Backend provides: `backendData.calculated.gpm`
   - Not currently displayed anywhere in UI
   - Could add to status panel or as inline gauge

6. **Approach Temperature** (Missing display)
   - Backend provides: `backendData.calculated.approach_f`
   - Only shown in thermal stack component
   - Should be in main status/metrics area

## ❌ Missing Features

### Backend
- [ ] Pressure sensor reading (currently returns 0.0)
  - Need to add pressure sensor to ADS1115 channels in `sensor_manager.py`
  - Update `SENSOR_CONFIG` in `config.py` with pressure calibration
  
- [ ] Basin level sensor (not implemented)
  - Backend returns: `basinLevel: 0` (hardcoded)
  - UI displays: `system.basinLevel || 0`
  
- [ ] Return temperature sensor (currently calculated)
  - Option: Add physical sensor
  - Alternative: Keep calculation (valid engineering method)

### Frontend
- [ ] Error handling for failed API calls
  - Control buttons don't show errors
  - Need toast/notification system
  
- [ ] Offline state UI
  - WebSocket shows "OFFLINE" but controls still active
  - Should disable controls when disconnected
  
- [ ] Loading states
  - No spinner while waiting for first data
  
- [ ] Confirmation dialogs
  - Pump switch should confirm
  - Emergency stop should confirm

## 🔧 Configuration Needed

### Environment Variables
Currently hardcoded in files:

**Frontend** (`useWebSocket.ts`, `api.ts`):
```typescript
const WEBSOCKET_URL = 'ws://localhost:8000/ws';  // Development
const API_BASE_URL = 'http://localhost:8000';    // Development
```

Need `.env` file:
```bash
VITE_WS_URL=ws://raspberrypi.local/ws
VITE_API_URL=http://raspberrypi.local
```

**Backend** (`main.py`):
- CORS currently allows `*` (all origins)
- Should restrict to specific UI domain in production

### Deployment
- [ ] Build React app (`npm run build`)
- [ ] Deploy to Pi (`/home/pi/cooling-tower-ui/dist/`)
- [ ] Configure Caddy to serve static files
- [ ] Test WebSocket through Caddy proxy

## 📋 Next Steps (Priority Order)

### Phase 1: Complete Data Integration (30 min)
1. Replace simulated pressure with real sensor data
2. Replace simulated delta-T with calculated value  
3. Use backend wet bulb instead of local calc
4. Display GPM and approach temperature

### Phase 2: Add Pressure Sensor (1 hour)
1. Wire pressure sensor to ADS1115 channel
2. Update `sensor_manager.py` calibration
3. Test sensor readings
4. Verify UI displays correct pressure

### Phase 3: Error Handling (1 hour)
1. Add toast notification system
2. Catch API errors in control handlers
3. Disable controls when offline
4. Add loading states

### Phase 4: Production Deployment (1 hour)
1. Create `.env.production` file
2. Build React app
3. Deploy to Pi via SCP
4. Test through Caddy proxy
5. Verify WebSocket connection
6. Test all controls on real hardware

### Phase 5: Polish (Optional)
1. Add confirmation dialogs
2. Improve status messages
3. Add trend graphs (historical data)
4. Mobile responsive layout
5. Dark/light mode toggle

## 🐛 Known Issues

1. **Pump selection sync**: If backend pump state changes externally, UI selector won't update until next WebSocket message (500ms delay) - acceptable

2. **Fan setpoint**: When switching from AUTO to MANUAL, fan keeps current Hz but UI doesn't show it as setpoint

3. **No reconnection feedback**: When WebSocket reconnects, no notification to user

4. **Stale data indicator**: If WebSocket stops but doesn't disconnect, UI shows stale data with no warning

## 💡 Future Enhancements

- **Alarm system**: Audible/visual alerts for critical conditions
- **Historical trends**: Store data in TimescaleDB, display graphs
- **Remote access**: VPN or secure tunnel for off-site monitoring
- **Mobile app**: React Native version
- **Multi-tower support**: Expand to control multiple towers
- **Maintenance scheduler**: Track runtime hours, suggest maintenance
- **Energy reporting**: Calculate kWh usage, efficiency metrics
