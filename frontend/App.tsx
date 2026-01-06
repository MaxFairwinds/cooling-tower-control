import React, { useState, useEffect } from 'react';
import { 
  Droplets,
  Fan,
  Activity,
  Zap,
  Thermometer,
  BarChart3,
  Power,
  Settings2,
  AlertTriangle,
  Info,
  ArrowDownToLine,
  Waves,
  Gauge,
  CheckCircle2,
  AlertOctagon,
  XCircle,
  WifiOff
} from 'lucide-react';
import { Card } from './components/Card';
import { VFDState, SystemState, ControlSettings } from './types';
import { useWebSocket } from './hooks/useWebSocket';
import api from './lib/api';

// Visual Components
import { PipeFluid, Flange, TeeFitting, CheckValve, ThreeWayValve } from './components/scada/PipingElements';
import { InlineDigitalGauge, AnalogPressureGauge } from './components/scada/Instruments';
import { InlinePump } from './components/scada/InlinePump';
import { WSHP } from './components/scada/WSHP';
import { CoolingTowerGraphic } from './components/scada/CoolingTower';
import { PumpSelector, TowerSelector, FanController } from './components/scada/Controls';

type PumpSelection = 'P-101' | 'OFF' | 'P-102';
type TowerSelection = 'ON' | 'OFF';

// --- NEW THERMAL STACK VISUALIZER ---
const ThermalStack: React.FC<{ 
    currentTemp: number; 
    wetBulbTemp: number; 
}> = ({ currentTemp, wetBulbTemp }) => {
    // Config
    const height = 300;
    const width = 240;
    const padding = 30;
    const minT = 30;
    const maxT = 120;
    const range = maxT - minT;
    
    const getY = (val: number) => {
        const clamped = Math.min(Math.max(val, minT), maxT);
        const pct = (clamped - minT) / range;
        return (height - padding) - (pct * (height - (padding * 2)));
    };

    // Thresholds
    const tripY = getY(105);
    const warnY = getY(90);
    const optY = getY(60);
    const heatY = getY(45);

    const currY = getY(currentTemp);
    const wbY = getY(wetBulbTemp);
    const approach = currentTemp - wetBulbTemp;

    // Status Colors
    let statusColor = "#10b981"; // Emerald
    let statusText = "OPTIMAL";
    let glowClass = "shadow-[0_0_10px_rgba(16,185,129,0.5)]";
    
    if (currentTemp > 105) { statusColor = "#ef4444"; statusText = "CRITICAL HIGH"; glowClass = "shadow-[0_0_15px_rgba(239,68,68,0.8)]"; }
    else if (currentTemp > 90) { statusColor = "#f59e0b"; statusText = "WARNING HIGH"; glowClass = "shadow-[0_0_10px_rgba(245,158,11,0.5)]"; }
    else if (currentTemp < 45) { statusColor = "#3b82f6"; statusText = "FREEZE RISK"; glowClass = "shadow-[0_0_15px_rgba(59,130,246,0.8)]"; }
    else if (currentTemp < 60) { statusColor = "#06b6d4"; statusText = "WARNING LOW"; glowClass = "shadow-[0_0_10px_rgba(6,182,212,0.5)]"; }

    return (
        <div className="flex flex-col gap-2 p-0 rounded-lg w-full relative">
             {/* Header */}
             <div className="flex items-center justify-between px-2 py-1 bg-slate-800/50 rounded border border-slate-700/50">
                 <div className="flex flex-col">
                    <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">THERMAL PROFILE</span>
                 </div>
                 <Activity size={14} className="text-slate-500" />
            </div>

            <div className="relative w-full h-[300px] bg-[#020617] rounded-md border border-slate-800 shadow-inner overflow-hidden select-none">
                <svg width="100%" height="100%" viewBox={`0 0 ${width} ${height}`}>
                    <defs>
                        {/* Improved High Contrast Grid Pattern */}
                        <pattern id="grid-pattern" width="20" height="20" patternUnits="userSpaceOnUse">
                            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#64748b" strokeWidth="0.8" opacity="0.4" />
                        </pattern>
                        
                        <linearGradient id="bar-gloss" x1="0" y1="0" x2="1" y2="0">
                            <stop offset="0%" stopColor="white" stopOpacity="0.05" />
                            <stop offset="50%" stopColor="white" stopOpacity="0.1" />
                            <stop offset="100%" stopColor="white" stopOpacity="0.05" />
                        </linearGradient>

                        {/* NEW: Optimal Zone Gradient */}
                        <linearGradient id="optimal-zone-grad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#10b981" stopOpacity="0.05" />
                            <stop offset="30%" stopColor="#10b981" stopOpacity="0.2" />
                            <stop offset="70%" stopColor="#10b981" stopOpacity="0.2" />
                            <stop offset="100%" stopColor="#10b981" stopOpacity="0.05" />
                        </linearGradient>

                        {/* Full Spectrum Thermal Gradient for the sidebar */}
                        <linearGradient id="thermal-gradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#ef4444" /> {/* 120F - Red */}
                            <stop offset="20%" stopColor="#f97316" /> {/* ~102F - Orange */}
                            <stop offset="40%" stopColor="#10b981" /> {/* ~84F - Green */}
                            <stop offset="60%" stopColor="#06b6d4" /> {/* ~66F - Cyan */}
                            <stop offset="85%" stopColor="#3b82f6" /> {/* ~43F - Blue */}
                            <stop offset="100%" stopColor="#6366f1" /> {/* 30F - Indigo */}
                        </linearGradient>

                        {/* Background Radial Glow */}
                        <radialGradient id="bg-glow" cx="50%" cy="50%" r="60%">
                            <stop offset="0%" stopColor="#1e293b" stopOpacity="0.4" />
                            <stop offset="100%" stopColor="#020617" stopOpacity="0" />
                        </radialGradient>

                         <filter id="glow-text">
                             <feDropShadow dx="0" dy="0" stdDeviation="2" floodColor={statusColor} floodOpacity="0.5"/>
                        </filter>
                        
                        <filter id="bar-glow">
                             <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                             <feMerge>
                                <feMergeNode in="coloredBlur"/>
                                <feMergeNode in="SourceGraphic"/>
                             </feMerge>
                        </filter>
                    </defs>

                    {/* Backgrounds */}
                    <rect width="100%" height="100%" fill="url(#bg-glow)" />
                    <rect width="100%" height="100%" fill="url(#grid-pattern)" />
                    
                    {/* NEW: Optimal Zone Overlay */}
                    <g>
                        <rect 
                            x="25" 
                            y={warnY} 
                            width={width - 60} 
                            height={optY - warnY} 
                            fill="url(#optimal-zone-grad)" 
                        />
                         {/* Subtle corner markers for the zone */}
                         <path d={`M 25 ${warnY} L 35 ${warnY} M 25 ${warnY} L 25 ${warnY + 10}`} stroke="#10b981" strokeWidth="1" opacity="0.5" fill="none" />
                         <path d={`M ${width - 35} ${warnY} L ${width - 45} ${warnY} M ${width - 35} ${warnY} L ${width - 35} ${warnY + 10}`} stroke="#10b981" strokeWidth="1" opacity="0.5" fill="none" />
                         <path d={`M 25 ${optY} L 35 ${optY} M 25 ${optY} L 25 ${optY - 10}`} stroke="#10b981" strokeWidth="1" opacity="0.5" fill="none" />
                         <path d={`M ${width - 35} ${optY} L ${width - 45} ${optY} M ${width - 35} ${optY} L ${width - 35} ${optY - 10}`} stroke="#10b981" strokeWidth="1" opacity="0.5" fill="none" />
                         
                         <text 
                            x={width / 2} 
                            y={warnY + (optY - warnY)/2 + 4} 
                            textAnchor="middle" 
                            className="text-[12px] font-bold fill-emerald-400 opacity-40 tracking-[0.4em]"
                         >
                            OPTIMAL
                        </text>
                    </g>
                    
                    {/* Thermal Bar (Left Side) */}
                    <g transform="translate(15, 0)">
                        {/* Glow behind bar */}
                        <rect x="-2" y={padding} width="10" height={height - padding*2} fill="url(#thermal-gradient)" opacity="0.2" filter="blur(4px)" />
                        
                        {/* Main Gradient Bar */}
                        <rect x="0" y={padding} width="6" height={height - padding*2} rx="3" fill="url(#thermal-gradient)" />
                        
                        {/* Gloss Overlay */}
                        <rect x="0" y={padding} width="6" height={height - padding*2} rx="3" fill="url(#bar-gloss)" />
                        
                        {/* Tick Marks on Bar */}
                        {[105, 90, 60, 45].map(t => (
                            <line key={t} x1="-2" y1={getY(t)} x2="8" y2={getY(t)} stroke="#020617" strokeWidth="1.5" />
                        ))}
                    </g>

                    {/* Zone Limit Lines - Colored to match the gradient sections */}
                    <line x1="25" y1={tripY} x2={width-40} y2={tripY} stroke="#ef4444" strokeWidth="1" strokeDasharray="3 3" opacity="0.6" />
                    <line x1="25" y1={warnY} x2={width-40} y2={warnY} stroke="#f97316" strokeWidth="1" strokeDasharray="3 3" opacity="0.5" />
                    <line x1="25" y1={optY} x2={width-40} y2={optY} stroke="#10b981" strokeWidth="1" strokeDasharray="3 3" opacity="0.5" />
                    <line x1="25" y1={heatY} x2={width-40} y2={heatY} stroke="#3b82f6" strokeWidth="1" strokeDasharray="3 3" opacity="0.5" />

                    {/* Central Axis */}
                    <line x1={width/2} y1={padding} x2={width/2} y2={height-padding} stroke="#334155" strokeWidth="1" />

                    {/* Scale Ticks (Right) */}
                    <g transform={`translate(${width - 35}, 0)`}>
                         {[120, 105, 90, 75, 60, 45, 30].map(val => (
                             <g key={val} transform={`translate(0, ${getY(val)})`}>
                                 <line x1="0" y1="0" x2="6" y2="0" stroke="#64748b" />
                                 <text x="10" y="3" className="text-[9px] font-mono fill-slate-500 font-bold">{val}</text>
                             </g>
                         ))}
                    </g>
                    
                    {/* WET BULB INDICATOR (Anchor) */}
                    <g transform={`translate(0, ${wbY})`}>
                         <line x1="40" y1="0" x2={width-40} y2="0" stroke="#38bdf8" strokeWidth="1.5" strokeDasharray="4 2" opacity="0.6" />
                         <rect x={width/2 - 25} y="-8" width="50" height="16" rx="4" fill="#0f172a" stroke="#38bdf8" strokeWidth="1.5" />
                         <text x={width/2} y="3" textAnchor="middle" className="text-[9px] font-mono font-bold fill-sky-400">WB {wetBulbTemp.toFixed(1)}</text>
                    </g>

                    {/* APPROACH BEAM */}
                    <path 
                        d={`M ${width/2 - 2} ${currY} L ${width/2 + 2} ${currY} L ${width/2 + 2} ${wbY} L ${width/2 - 2} ${wbY} Z`}
                        fill={statusColor}
                        opacity="0.3"
                    />

                    {/* CURRENT TEMP INDICATOR (Slider) */}
                    <g transform={`translate(0, ${currY})`} className="transition-all duration-300 ease-out">
                         {/* Glow effect under the cursor */}
                         <ellipse cx={width/2} cy="0" rx="60" ry="15" fill={statusColor} opacity="0.2" filter="blur(10px)" />
                         
                         {/* Cursor Body */}
                         <path d={`M ${width/2 - 50} 0 L ${width/2 - 40} -12 L ${width/2 + 40} -12 L ${width/2 + 50} 0 L ${width/2 + 40} 12 L ${width/2 - 40} 12 Z`} fill="#0f172a" stroke={statusColor} strokeWidth="1.5" />
                         <path d={`M ${width/2 - 50} 0 L ${width/2 - 40} -12 L ${width/2 + 40} -12 L ${width/2 + 50} 0 L ${width/2 + 40} 12 L ${width/2 - 40} 12 Z`} fill="url(#bar-gloss)" opacity="0.5" />

                         {/* Side Arrows */}
                         <path d={`M ${width/2 - 58} 0 L ${width/2 - 50} 0`} stroke={statusColor} strokeWidth="2" />
                         <path d={`M ${width/2 + 58} 0 L ${width/2 + 50} 0`} stroke={statusColor} strokeWidth="2" />
                         
                         {/* Connecting line to the main thermal bar */}
                         <line x1={20} y1="0" x2={width/2 - 50} y2="0" stroke={statusColor} strokeWidth="1" strokeDasharray="1 3" opacity="0.5" />

                         {/* Text Value */}
                         <text x={width/2} y="4" textAnchor="middle" className="text-[14px] font-mono font-bold fill-white tracking-widest" filter="url(#glow-text)">
                             {currentTemp.toFixed(1)}°
                         </text>
                    </g>

                </svg>
            </div>

             {/* Footer Stats */}
             <div className="grid grid-cols-2 gap-2">
                 {/* Approach Stat */}
                 <div className="bg-slate-900 p-2 rounded border border-slate-700/50 flex flex-col justify-center items-center relative overflow-hidden group shadow-md">
                     <div className="absolute inset-0 bg-gradient-to-b from-transparent to-slate-800/30 pointer-events-none"></div>
                     <div className="absolute top-0 left-0 w-full h-[1px] bg-gradient-to-r from-transparent via-sky-500 to-transparent opacity-20"></div>
                     <span className="text-[8px] text-slate-500 uppercase tracking-widest font-bold z-10">APPROACH</span>
                     <div className="flex items-baseline gap-1 z-10">
                        <span className={`text-lg font-mono font-bold ${approach < 7.5 ? 'text-emerald-400' : 'text-slate-200'}`}>
                            {approach.toFixed(1)}
                        </span>
                        <span className="text-[9px] text-slate-500">°F</span>
                     </div>
                 </div>

                 {/* Status Stat */}
                 <div className={`p-2 rounded border flex flex-col justify-center items-center transition-colors duration-300 ${glowClass} bg-slate-900 border-slate-700/50 shadow-md relative overflow-hidden`}>
                     <div className="absolute inset-0 bg-gradient-to-b from-transparent to-slate-800/30 pointer-events-none"></div>
                     <span className="text-[8px] text-slate-500 uppercase tracking-widest font-bold z-10">STATUS</span>
                     <span className="text-[10px] font-bold tracking-tight z-10" style={{ color: statusColor }}>
                            {statusText}
                     </span>
                 </div>
             </div>
        </div>
    );
};


export const App: React.FC = () => {
  // SAFETY: Read-only mode during testing - disable all controls
  const READ_ONLY_MODE = true;
  
  // Connect to WebSocket backend
  const { data: backendData, isConnected, error } = useWebSocket();
  
  // State for Selectors (UI only - actual control via API)
  const [pumpSelection, setPumpSelection] = useState<PumpSelection>('P-101');
  const [towerSelection, setTowerSelection] = useState<TowerSelection>('OFF');

  // Show loading screen until first data arrives
  if (!backendData && isConnected) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-900">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-sky-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-slate-400 font-bold">Loading system data...</p>
        </div>
      </div>
    );
  }

  // Show offline screen if not connected and no cached data
  if (!backendData && !isConnected) {
    return (
      <div className="flex items-center justify-center h-screen bg-slate-900">
        <div className="text-center">
          <WifiOff size={48} className="text-red-500 mx-auto mb-4" />
          <p className="text-red-400 font-bold text-xl mb-2">Backend Offline</p>
          <p className="text-slate-500">Waiting for connection...</p>
          {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
        </div>
      </div>
    );
  }

  // Derived state from backend data
  const [vfdPrimary, setVfdPrimary] = useState<VFDState>({
    id: 'p1', name: 'Primary Pump', status: 'Stopped', frequency: 0, current: 0, setpoint: 45, manualMode: false
  });
  const [vfdBackup, setVfdBackup] = useState<VFDState>({
    id: 'p2', name: 'Backup Pump', status: 'Stopped', frequency: 0, current: 0, setpoint: 45, manualMode: false
  });
  const [vfdTower, setVfdTower] = useState<VFDState>({
    id: 'ct1', name: 'Tower Fan', status: 'Stopped', frequency: 0, current: 0, setpoint: 0, manualMode: true
  });
  
  const [system, setSystem] = useState<SystemState>({
    isRunning: false,
    autoControl: false,
    activePump: 'PRIMARY',
    temperature: 0,
    basinLevel: 0,
    outdoorTemp: 0,
    humidity: 0,
    heatLoad: 0,
    lastUpdate: new Date(),
  });

  // Map WebSocket data to UI state
  useEffect(() => {
    if (!backendData) return;

    try {
      // Map fan VFD
      setVfdTower({
        id: 'ct1',
        name: 'Tower Fan',
        status: backendData.fan.state as any,
        frequency: backendData.fan.frequency,
        current: backendData.fan.current,
        setpoint: backendData.fan_setpoint,
        manualMode: !backendData.fan_auto_mode
      });

      // Map pump VFDs
      setVfdPrimary({
        id: 'p1',
        name: 'Primary Pump',
        status: backendData.pump_primary.state as any,
        frequency: backendData.pump_primary.frequency,
        current: backendData.pump_primary.current,
        setpoint: backendData.pump_primary.frequency, // Current freq is setpoint in manual
        manualMode: true
      });

      setVfdBackup({
        id: 'p2',
        name: 'Backup Pump',
        status: backendData.pump_backup.state as any,
        frequency: backendData.pump_backup.frequency,
        current: backendData.pump_backup.current,
        setpoint: backendData.pump_backup.frequency,
        manualMode: true
      });

      // Update system state
      setSystem({
        isRunning: backendData.pump_primary.state === 'Running' || backendData.pump_backup.state === 'Running',
        autoControl: backendData.fan_auto_mode,
        activePump: backendData.active_pump === 'primary' ? 'PRIMARY' : 'BACKUP',
        temperature: backendData.sensors.basin_temp_f,
        basinLevel: 0, // No sensor yet
        outdoorTemp: backendData.weather.outdoor_temp_f,
        humidity: backendData.weather.humidity_pct,
        heatLoad: backendData.calculated.heat_load_kw,
        lastUpdate: new Date(backendData.sensors.timestamp)
      });

      // Sync selectors with backend state
      setPumpSelection(
        backendData.pump_primary.state === 'Running' ? 'P-101' :
        backendData.pump_backup.state === 'Running' ? 'P-102' :
        'OFF'
      );

      setTowerSelection(
        backendData.fan.state === 'Running' || backendData.fan_auto_mode ? 'ON' : 'OFF'
      );

    } catch (err) {
      console.error('[App] Failed to map backend data:', err);
    }
  }, [backendData]);

  // Control handlers - call API instead of local state
  const handlePumpSelection = async (value: PumpSelection) => {
    if (READ_ONLY_MODE) {
      alert('⚠️ READ-ONLY MODE: Controls are disabled during testing. System remains in manual mode.');
      return;
    }
    if (!isConnected) {
      console.warn('[Control] Cannot control pump while offline');
      return;
    }
    try {
      if (value === 'OFF') {
        await api.pump.stop();
      } else {
        // Switch pump if needed
        const targetPump = value === 'P-101' ? 'primary' : 'backup';
        if (targetPump !== backendData?.active_pump) {
          await api.pump.switch();
        }
        // Ensure pump is running
        await api.pump.start();
      }
      setPumpSelection(value); // Update UI immediately
    } catch (err) {
      console.error('[Control] Pump selection failed:', err);
      alert(`Pump control failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }READ_ONLY_MODE) {
      alert('⚠️ READ-ONLY MODE: Controls are disabled during testing. System remains in manual mode.');
      return;
    }
    if (
  };

  const handleTowerSelection = async (value: TowerSelection) => {
    if (!isConnected) {
      console.warn('[Control] Cannot control tower while offline');
      return;
    }
    try {
      if (value === 'ON') {
        // In manual mode, start fan at current setpoint
        if (vfdTower.manualMode && vfdTower.setpoint > 0) {
          await api.fan.setFrequency(vfdTower.setpoint);
        }
      } else {
        // Turn off
        await api.fan.setFrequency(0);
      }
      setTowerSelection(value); // Update UI immediately
    } catch (err) {
      console.error('[Control] Tower selection failed:', err);
      alert(`Tower control failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }READ_ONLY_MODE) {
      alert('⚠️ READ-ONLY MODE: Controls are disabled during testing. System remains in manual mode.');
      return;
    }
    if (
  };

  const handleFanModeToggle = async () => {
    if (!isConnected) {
      console.warn('[Control] Cannot change fan mode while offline');
      return;
    }
    try {
      const newMode = vfdTower.manualMode ? 'auto' : 'manual';
      await api.fan.setMode(newMode);
    } catch (err) {
      console.error('[Control] Fan mode toggle failed:', err);
      alert(`Fan mode change failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }READ_ONLY_MODE) {
      alert('⚠️ READ-ONLY MODE: Controls are disabled during testing. System remains in manual mode.');
      return;
    }
    if (
  };

  const handleFanSetHz = async (hz: number) => {
    if (!isConnected) {
      console.warn('[Control] Cannot set fan frequency while offline');
      return;
    }
    try {
      await api.fan.setFrequency(hz);
    } catch (err) {
      console.error('[Control] Fan frequency set failed:', err);
      alert(`Fan frequency set failed: ${err instanceof Error ? err.message : 'Unknown error'}`);
    }
  };

  // --- COORDINATE SYSTEM ---
  // Adjusted: Even Spacing Strategy (~45px gaps between key elements)
  const towerX = 130;  // Center
  const towerY = 10;
  
  const basinOutletX = 230; 
  
  const towerReturnInletXFinal = 235; 
  const towerReturnInletYFinal = 31;
  
  // Pump Assembly moved to fit grid:
  // Suction Header moved from 380 to 400
  // Pump moved from 453 to 473
  // Discharge Header moved from 625 to 645
  const suctionHeaderX = 400; 
  const pumpX = 473; 
  const dischargeHeaderX = 645; 
  
  // P-102 (SEC)
  const pump1Y = 178;
  // P-101 (PRI) 
  const pump2Y = 298; 
  
  // CENTERING LOGIC: Both tees should be centered on the vertical pump headers
  const headerCenterY = 238; // (178 + 298) / 2
  
  const basinOutletY = headerCenterY; // Aligns Suction Tee
  
  const wshpX = 880; 
  const wshpY = 198; 
  
  const wshpInletX = wshpX - 74;
  const wshpInletY = headerCenterY; // Aligns Discharge Tee
  
  const wshpOutletX = wshpX;
  const wshpOutletY = wshpY - 140; 

  const returnHeaderY = 25; 

  // --- DYNAMIC COLOR INTERPOLATION ---
  const interpolateRgb = (c1: number[], c2: number[], factor: number) => {
      const r = Math.round(c1[0] + factor * (c2[0] - c1[0]));
      const g = Math.round(c1[1] + factor * (c2[1] - c1[1]));
      const b = Math.round(c1[2] + factor * (c2[2] - c1[2]));
      return `rgb(${r},${g},${b})`;
  };

  const getSupplyColor = (t: number) => {
      // 5-Zone Temperature Gradient:
      // Red Below Optimal (<45): White -> Sky Blue
      // Yellow Below Optimal (45-60): Sky Blue -> Cyan
      // Optimal (60-90): Cyan -> Medium Blue
      // Yellow Above Optimal (90-105): Medium Blue -> Orange
      // Red Above Optimal (>105): Orange -> Red
      const stops = [
          { temp: 40, color: [255, 255, 255] },   // White
          { temp: 45, color: [56, 189, 248] },    // Sky Blue (#38bdf8)
          { temp: 60, color: [6, 182, 212] },     // Cyan (#06b6d4)
          { temp: 90, color: [59, 130, 246] },    // Medium Blue (#3b82f6)
          { temp: 105, color: [249, 115, 22] },   // Orange (#f97316)
          { temp: 120, color: [239, 68, 68] }     // Red (#ef4444)
      ];

      if (t <= stops[0].temp) return `rgb(${stops[0].color.join(',')})`;
      if (t >= stops[stops.length - 1].temp) return `rgb(${stops[stops.length - 1].color.join(',')})`;
      
      for (let i = 0; i < stops.length - 1; i++) {
          const s1 = stops[i];
          const s2 = stops[i + 1];
          if (t >= s1.temp && t < s2.temp) {
              const factor = (t - s1.temp) / (s2.temp - s1.temp);
              return interpolateRgb(s1.color, s2.color, factor);
          }
      }
      return 'rgb(6, 182, 212)'; // Default Cyan
  };

  const getReturnColor = (t: number) => {
      // Adjusted for Fahrenheit
      const stops = [
          { temp: 60, color: [59, 130, 246] },    // Blue 500
          { temp: 75, color: [249, 115, 22] },    // Orange 500
          { temp: 86, color: [239, 68, 68] },     // Red 500
          { temp: 113, color: [153, 27, 27] }      // Red 800
      ];
      if (t <= stops[0].temp) return `rgb(${stops[0].color.join(',')})`;
      if (t >= stops[stops.length - 1].temp) return `rgb(${stops[stops.length - 1].color.join(',')})`;
      for (let i = 0; i < stops.length - 1; i++) {
          const s1 = stops[i];
          const s2 = stops[i + 1];
          if (t >= s1.temp && t < s2.temp) {
              const factor = (t - s1.temp) / (s2.temp - s1.temp);
              return interpolateRgb(s1.color, s2.color, factor);
          }
      }
      return 'rgb(249, 115, 22)';
  };

  const supplyTemp = system.temperature;
  const activePump = system.activePump === 'PRIMARY' ? vfdPrimary : vfdBackup;
  const flowFactor = activePump.status === 'Running' ? (activePump.frequency / 60) : 0;
  
  // Use calculated delta-T from backend
  const returnTemp = backendData?.calculated.return_temp_f || (supplyTemp + 1.0);
  const visualDeltaT = returnTemp - supplyTemp;
  
  const supplyColor = getSupplyColor(supplyTemp);
  const returnColor = getReturnColor(returnTemp);
  
  // Use real pressure sensor from backend
  const dischargePressure = backendData?.sensors.pressure_psi || 0;

  // Use calculated wet bulb from backend
  const currentWetBulb = backendData?.weather.wet_bulb_f || 0;
  
  // Get flow rate from backend calculations
  const currentGPM = backendData?.calculated.gpm || 0;

  // --- STEAM INTENSITY CALCULATION ---
  // Steam Plume = (Water Temp - Outdoor Temp) * Airflow
  // The colder the air (and hotter the water), the more steam.
  // Normalized to 0-1 range.
  // Assume max delta ~50F (90F water, 40F air)
  const deltaT = Math.max(0, system.temperature - system.outdoorTemp);
  const fanRatio = vfdTower.frequency / 60;
  const steamIntensity = Math.min(1, Math.max(0, (deltaT * fanRatio) / 25));

  // --- WSHP AIR SIDE CALCULATION ---
  // Room Return Air is 75°F.
  // Target Discharge is 55°F.
  
  // Daikin Spec: 
  // Green Zone ends at 90°F (Optimal).
  // Trip point is 105°F.
  
  const ROOM_TEMP = 75.0;
  const TARGET_LAT = 55.0;
  const TRIP_POINT = 105.0;
  const EFFICIENCY_KNEE = 90.0; // Where performance starts dropping

  const waterLoopSafe = system.temperature < TRIP_POINT;
  const wshpRunning = system.isRunning && waterLoopSafe;
  
  let dischargeAirTemp = ROOM_TEMP;
  
  if (wshpRunning) {
      if (system.temperature <= EFFICIENCY_KNEE) {
          // In the Green Zone (or lower), unit maintains 55°F easily.
          // Note: If EWT is extremely low (<45), unit might freeze, but for air temp simulation we assume 55F until failure.
          dischargeAirTemp = TARGET_LAT;
      } else {
          // In the Yellow Zone (90-105), Head pressure rises, volumetric efficiency drops.
          // The unit cannot reject enough heat to maintain 55°F LAT.
          // Simulation: LAT rises by ~0.6°F for every 1°F the water is above 90.
          const excessHeat = system.temperature - EFFICIENCY_KNEE;
          const penalty = excessHeat * 0.6; 
          dischargeAirTemp = Math.min(TARGET_LAT + penalty, ROOM_TEMP);
      }
  }

  // Pipe Data Configuration - CONSOLIDATED PATHS
  const pipes = [
      // 1. COMMON SUCTION (Basin -> Suction Header Tee)
      { 
          d: `M ${basinOutletX} ${basinOutletY} L ${suctionHeaderX} ${basinOutletY}`, 
          isRunning: system.isRunning, 
          flowColor: supplyColor 
      },
      
      // 2. PUMP 1 BRANCH (Upper Loop: Tee -> P1 -> Tee)
      // Path: Suction Tee -> Up to P1 -> Right to P1 -> Right to Header -> Down to Discharge Tee
      { 
          d: `M ${suctionHeaderX} ${basinOutletY} L ${suctionHeaderX} ${pump1Y} L ${pumpX} ${pump1Y} L ${dischargeHeaderX} ${pump1Y} L ${dischargeHeaderX} ${wshpInletY}`, 
          isRunning: vfdBackup.status === 'Running', 
          flowColor: supplyColor 
      },

      // 3. PUMP 2 BRANCH (Lower Loop: Tee -> P2 -> Tee)
      // Path: Suction Tee -> Down to P2 -> Right to P2 -> Right to DischHeader (298) -> Up to DischTee (238)
      { 
          d: `M ${suctionHeaderX} ${basinOutletY} L ${suctionHeaderX} ${pump2Y} L ${pumpX} ${pump2Y} L ${dischargeHeaderX} ${pump2Y} L ${dischargeHeaderX} ${wshpInletY}`, 
          isRunning: vfdPrimary.status === 'Running', 
          flowColor: supplyColor 
      },

      // 4. COMMON DISCHARGE (Discharge Tee -> WSHP)
      { 
          d: `M ${dischargeHeaderX} ${wshpInletY} L ${wshpInletX} ${wshpInletY}`, 
          isRunning: system.isRunning, 
          flowColor: supplyColor 
      },

      // 5. RETURN LINE (Already consolidated)
      { 
          d: `M ${wshpOutletX} ${wshpOutletY} L ${wshpOutletX} ${returnHeaderY} L ${towerReturnInletXFinal} ${returnHeaderY} L ${towerReturnInletXFinal} ${towerReturnInletYFinal}`, 
          isRunning: system.isRunning, 
          flowColor: returnColor 
      }
  ];

  // --- SYSTEM STATUS LOGIC ---
  let sysStatus: 'OPTIMAL' | 'WARNING' | 'CRITICAL' | 'OFFLINE' = 'OFFLINE';
  let statusMsg = "SYSTEM STOPPED";
  let statusIcon = AlertOctagon;
  let statusColorText = "text-slate-400";
  let statusColorBg = "bg-slate-500/10";
  let statusBorder = "border-slate-500";
  let statusGlow = "shadow-[0_0_15px_rgba(100,116,139,0.2)]";

  if (system.isRunning) {
      if (system.temperature > 105) {
          sysStatus = 'CRITICAL';
          statusMsg = "HIGH TEMP TRIP";
          statusIcon = XCircle;
          statusColorText = "text-rose-500";
          statusColorBg = "bg-rose-500/10";
          statusBorder = "border-rose-500";
          statusGlow = "shadow-[0_0_20px_rgba(244,63,94,0.4)]";
      } else if (system.temperature < 45) {
          sysStatus = 'CRITICAL';
          statusMsg = "FREEZE WARNING";
          statusIcon = XCircle;
          statusColorText = "text-rose-500";
          statusColorBg = "bg-rose-500/10";
          statusBorder = "border-rose-500";
          statusGlow = "shadow-[0_0_20px_rgba(244,63,94,0.4)]";
      } else if (system.temperature > 90) {
          sysStatus = 'WARNING';
          statusMsg = "HIGH DISCHARGE TEMP";
          statusIcon = AlertTriangle;
          statusColorText = "text-amber-500";
          statusColorBg = "bg-amber-500/10";
          statusBorder = "border-amber-500";
          statusGlow = "shadow-[0_0_15px_rgba(245,158,11,0.3)]";
      } else if (system.temperature < 60) {
          sysStatus = 'WARNING';
          statusMsg = "LOW LOOP TEMP";
          statusIcon = AlertTriangle;
          statusColorText = "text-amber-500";
          statusColorBg = "bg-amber-500/10";
          statusBorder = "border-amber-500";
          statusGlow = "shadow-[0_0_15px_rgba(245,158,11,0.3)]";
      } else {
          sysStatus = 'OPTIMAL';
          statusMsg = "OPTIMAL OPERATION";
          statusIcon = CheckCircle2;
          statusColorText = "text-emerald-400";
          statusColorBg = "bg-emerald-500/10";
          statusBorder = "border-emerald-500";
          statusGlow = "shadow-[0_0_15px_rgba(16,185,129,0.3)]";
      }
  }

  return (
    <div className="flex flex-col h-screen bg-[#475569] bg-grid text-slate-200 overflow-hidden font-sans select-none relative">
       {/* Header */}
       <header className="h-14 bg-slate-900/80 border-b border-slate-700 flex items-center justify-between px-6 shrink-0 backdrop-blur-md z-30 shadow-md">
           <div className="flex items-center gap-4">
               <div className="w-8 h-8 bg-sky-500 rounded flex items-center justify-center text-slate-900">
                   <Droplets size={20} />
               </div>
               <div>
                   <h1 className="text-lg font-bold tracking-tight text-white leading-none">5913 WATER LOOP</h1>
                   <div className="text-[10px] text-slate-400 font-bold tracking-widest uppercase">COOLING TOWER 01</div>
               </div>
           </div>
           
           <div className="flex items-center gap-6">
                {/* BACKEND CONNECTION STATUS */}
                <div className="flex items-center gap-2">
                    {isConnected ? (
                        <>
                            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                            <span className="text-[10px] text-emerald-400 font-bold">CONNECTED</span>
                        </>
                    ) : (
                        <>
                            <WifiOff size={14} className="text-red-500" />
                            <span className="text-[10px] text-red-400 font-bold">{error ? 'ERROR' : 'OFFLINE'}</span>
                        </>
                    )}
                </div>

                {/* FLOW RATE (GPM) */}
                <div className="flex flex-col items-center">
                    <span className="text-[10px] text-slate-400 font-bold">FLOW RATE</span>
                    <span className="text-xs font-mono font-bold text-cyan-400">{currentGPM.toFixed(0)} GPM</span>
                </div>

                {/* WEATHER DATA (Read-only from API) */}
                <div className="flex flex-col items-center">
                    <span className="text-[10px] text-slate-400 font-bold">OUTDOOR</span>
                    <span className="text-xs font-mono font-bold text-sky-400">{system.outdoorTemp.toFixed(1)}°F</span>
                </div>

                {/* HUMIDITY (Read-only from API) */}
                <div className="flex flex-col items-center">
                    <span className="text-[10px] text-slate-400 font-bold">HUMIDITY</span>
                    <span className="text-xs font-mono font-bold text-sky-400">{system.humidity.toFixed(0)}%</span>
                </div>

                {/* APPROACH TEMPERATURE */}
                <div className="flex flex-col items-center">
                    <span className="text-[10px] text-slate-400 font-bold">APPROACH</span>
                    <span className="text-xs font-mono font-bold text-emerald-400">{(backendData?.calculated.approach_f || 0).toFixed(1)}°F</span>
                </div>

                {/* HEAT LOAD (Calculated from sensors) */}
                <div className="flex flex-col items-center">
                    <span className="text-[10px] text-slate-400 font-bold">HEAT LOAD</span>
                    <span className="text-xs font-mono font-bold text-amber-400">{(system.heatLoad || 0).toFixed(0)} kW</span>
                </div>

                <div className="h-8 w-px bg-slate-700"></div>

                <div className="flex flex-col items-end">
                    <span className="text-[10px] text-slate-400 font-bold">SYSTEM TIME</span>
                    <span className="text-xs font-mono font-bold text-sky-400">{system.lastUpdate.toLocaleTimeString()}</span>
                </div>
                <div className="h-8 w-px bg-slate-700"></div>
                <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${system.isRunning ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`}></div>
                    <span className="text-xs font-bold tracking-wide text-slate-300">{system.isRunning ? 'SYSTEM ACTIVE' : 'SYSTEM STOPPED'}</span>
                </div>
           </div>
       </header>

       {/* Main Layout Area */}
       <div className="flex-1 flex overflow-hidden relative">
           
           {/* LEFT SIDEBAR */}
           <aside className="w-72 bg-slate-900/95 border-r border-slate-700/50 flex flex-col p-4 gap-6 backdrop-blur-sm z-20 shadow-xl overflow-y-auto">
                {/* Section Title */}
                <div className="flex items-center gap-2 pb-2 border-b border-slate-700/50">
                    <Settings2 className="text-sky-500" size={16} />
                    <h2 className="text-sm font-bold text-slate-200 tracking-wider">LOOP CONTROLS</h2>
                </div>

                {/* 1. TOWER CONTROL TOGGLE */}
                <div className="bg-slate-800/40 rounded-lg p-3 border border-slate-700/50">
                    <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                            <Fan size={14} className="text-slate-400" />
                            <span className="text-xs font-bold text-slate-300">TOWER FAN MODE</span>
                        </div>
                        <div className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${vfdTower.manualMode ? 'bg-amber-500/10 text-amber-500 border-amber-500/20' : 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'}`}>
                            {vfdTower.manualMode ? 'MANUAL' : 'AUTO PID'}
                        </div>
                    </div>

                    <div className="flex bg-slate-900 rounded p-1 border border-slate-700 relative">
                        {/* Toggle Background Slider */}
                        <div className={`absolute top-1 bottom-1 w-[calc(50%-4px)] bg-slate-700 rounded transition-all duration-300 ${vfdTower.manualMode ? 'left-1 bg-amber-600' : 'left-[calc(50%+2px)] bg-emerald-600'}`}></div>
                        
                        <button 
                            onClick={() => api.fan.setMode('manual')}
                            className={`flex-1 relative z-10 text-[10px] font-bold py-1.5 text-center transition-colors ${vfdTower.manualMode ? 'text-white' : 'text-slate-500'}`}
                        >
                            MANUAL
                        </button>
                        <button 
                             onClick={() => api.fan.setMode('auto')}
                             className={`flex-1 relative z-10 text-[10px] font-bold py-1.5 text-center transition-colors ${!vfdTower.manualMode ? 'text-white' : 'text-slate-500'}`}
                        >
                            AUTO
                        </button>
                    </div>
                    
                    <div className="mt-3 text-[10px] text-slate-500 leading-tight">
                        {vfdTower.manualMode 
                            ? "Operator sets fixed fan speed Hz via field controller." 
                            : "System automatically modulates fan speed to maintain target temperature."}
                    </div>
                </div>

                {/* 2. DYNAMIC THERMAL STACK (Replaces Old Chart) */}
                <ThermalStack 
                    currentTemp={system.temperature} 
                    wetBulbTemp={currentWetBulb}
                />

           </aside>

           {/* MAIN GRAPHIC AREA */}
           <div className="flex-1 relative bg-transparent overflow-hidden flex items-center justify-center p-4">
                <svg width="100%" height="100%" viewBox="0 -40 1000 470" preserveAspectRatio="xMidYMid meet" className="w-full h-full drop-shadow-2xl">
                    <defs>
                        <filter id="component-shadow" x="-50%" y="-50%" width="200%" height="200%">
                             <feDropShadow dx="4" dy="4" stdDeviation="4" floodOpacity="0.5" floodColor="#000"/>
                        </filter>
                        
                        <linearGradient id="metallic-gradient" x1="0" y1="0" x2="1" y2="1">
                             <stop offset="0%" stopColor="#334155" />
                             <stop offset="30%" stopColor="#64748b" />
                             <stop offset="60%" stopColor="#94a3b8" />
                             <stop offset="100%" stopColor="#1e293b" />
                        </linearGradient>

                        <linearGradient id="industrial-metal" x1="0" y1="0" x2="1" y2="0">
                            <stop offset="0%" stopColor="#0f172a" /> 
                            <stop offset="10%" stopColor="#334155" /> 
                            <stop offset="50%" stopColor="#475569" /> 
                            <stop offset="90%" stopColor="#334155" />
                            <stop offset="100%" stopColor="#0f172a" />
                        </linearGradient>
                        
                        <linearGradient id="fan-blade-composite" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#334155" /> 
                            <stop offset="50%" stopColor="#64748b" /> 
                            <stop offset="100%" stopColor="#1e293b" /> 
                        </linearGradient>
                    </defs>
                    
                    <g opacity="1" filter="url(#component-shadow)">
                        
                        {/* --- LAYER 1: PIPE STRUCTURE (Unified Rendering) --- */}
                        <g id="layer-pipe-structure">
                            {/* Pass 1: All Pipe Casings (Borders) */}
                            {pipes.map((pipe, index) => (
                                <path 
                                    key={`casing-${index}`} 
                                    d={pipe.d} 
                                    fill="none" 
                                    stroke="#0f172a" 
                                    strokeWidth={16} 
                                    strokeLinecap="round" 
                                    strokeLinejoin="round" 
                                />
                            ))}
                            {/* Pass 2: All Pipe Bodies (Interiors) */}
                            {pipes.map((pipe, index) => (
                                <path 
                                    key={`body-${index}`} 
                                    d={pipe.d} 
                                    fill="none" 
                                    stroke="#1e293b" 
                                    strokeWidth={12} 
                                    strokeLinecap="round" 
                                    strokeLinejoin="round" 
                                />
                            ))}
                        </g>

                        {/* --- LAYER 2: FITTINGS --- */}
                        <g id="layer-fittings">
                            <CheckValve x={pumpX + 60} y={pump1Y} rotation={0} />
                            <CheckValve x={pumpX + 60} y={pump2Y} rotation={0} />
                            <Flange x={wshpInletX} y={wshpInletY} orientation="vertical" />
                            <Flange x={wshpOutletX} y={wshpOutletY} orientation="horizontal" />
                        </g>

                        {/* --- LAYER 3: PIPE FLUID --- */}
                        <g id="layer-pipe-fluid">
                            {pipes.map((pipe, index) => (
                                <PipeFluid 
                                    key={`fluid-${index}`} 
                                    d={pipe.d} 
                                    isRunning={pipe.isRunning} 
                                    flowColor={pipe.flowColor} 
                                />
                            ))}
                        </g>
                        
                        {/* --- LAYER 3.5: TOP FITTINGS --- */}
                        <g id="layer-fittings-top">
                             {/* Suction Header Valve (Inputs Left, outputs Up/Down) */}
                             <ThreeWayValve 
                                x={suctionHeaderX} 
                                y={basinOutletY} 
                                common="left" 
                                direction={pumpSelection === 'P-102' ? 'up' : 'down'}
                                flowColor={supplyColor}
                             />
                             {/* Discharge Header Valve (Inputs Up/Down, output Right) */}
                             <ThreeWayValve 
                                x={dischargeHeaderX} 
                                y={wshpInletY} 
                                common="right" 
                                direction={pumpSelection === 'P-102' ? 'up' : 'down'}
                                flowColor={supplyColor}
                             />
                        </g>

                        {/* --- LAYER 4: EQUIPMENT --- */}
                        <g id="layer-equipment">
                            <CoolingTowerGraphic 
                                x={towerX} y={towerY} 
                                waterLevel={true}
                                levelValue={system.basinLevel || 0}
                                tempValue={system.temperature}
                                isFanRunning={vfdTower.frequency > 0} 
                                isWaterFlowing={system.isRunning}
                                waterColor={supplyColor}
                                returnColor={returnColor}
                                steamIntensity={steamIntensity}
                                frequency={vfdTower.frequency}
                            />
                            
                            {/* Tower Selector Switch */}
                            <TowerSelector 
                                x={towerX + 11} 
                                y={425} 
                                value={towerSelection} 
                                onChange={handleTowerSelection} 
                            />
                            
                            {/* NEW FAN CONTROLLER - Appears to the right of the selector when ON */}
                            <FanController 
                                x={towerX + 130} 
                                y={425} 
                                enabled={towerSelection === 'ON' || !vfdTower.manualMode} 
                                manualMode={vfdTower.manualMode}
                                frequency={vfdTower.frequency}
                                setpoint={vfdTower.setpoint}
                                onToggleMode={handleFanModeToggle}
                                onSetHz={handleFanSetHz}
                            />

                            <InlinePump 
                                x={pumpX} y={pump1Y} 
                                status={vfdBackup.status} 
                                label="P-102 (SEC)" 
                                freq={vfdBackup.frequency}
                            />
                            
                            <InlinePump 
                                x={pumpX} y={pump2Y} 
                                status={vfdPrimary.status} 
                                label="P-101 (PRI)" 
                                freq={vfdPrimary.frequency}
                            />
                            
                            {/* Pump Selector Switch aligned with P-101 label center (pumpX + 60) and Tower Toggle (y=425) */}
                            <PumpSelector 
                                x={pumpX + 60} 
                                y={425} 
                                value={pumpSelection} 
                                onChange={handlePumpSelection} 
                                title="MANUAL SELECT"
                            />

                            <WSHP 
                                x={wshpX} 
                                y={wshpY} 
                                isRunning={system.isRunning} 
                                enteringWaterTemp={system.temperature}
                                dischargeAirTemp={dischargeAirTemp}
                            />

                            {/* Replaced AnalogGauges with InlineDigitalGauges */}
                            {/* Return Gauge moved to match vertical alignment of new supply gauge position */}
                            <InlineDigitalGauge 
                                x={320} 
                                y={returnHeaderY} 
                                value={returnTemp} 
                                label="RETURN" 
                                color={returnColor}
                            />
                            
                            {/* Supply Gauge 1 (Before Pumps) moved to 320 */}
                            <InlineDigitalGauge 
                                x={320} 
                                y={headerCenterY} 
                                value={supplyTemp} 
                                label="SUPPLY" 
                                color={supplyColor}
                            />

                            {/* REPLACED: Duplicate Supply Gauge with ANALOG PRESSURE GAUGE */}
                            <AnalogPressureGauge 
                                x={725} 
                                y={wshpInletY} 
                                value={dischargePressure} 
                                label="PSI" 
                                max={80}
                            />
                        </g>

                    </g>
                </svg>
           </div>
           
           {/* --- NEW SIMPLIFIED STATUS CARD (Bottom Right) --- */}
           {/* Sleek, shorter glass panel */}
           <div className="absolute bottom-6 right-6 z-40">
               <div className="bg-slate-900/90 backdrop-blur-md border border-slate-700/50 rounded-lg shadow-2xl p-3 flex items-center gap-6 min-w-[320px]">
                    
                    {/* Status Section */}
                    <div className="flex items-center gap-3">
                         <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${statusColorBg} border ${statusBorder} shadow-lg`}>
                             {React.createElement(statusIcon, { size: 20, className: statusColorText })}
                         </div>
                         <div className="flex flex-col">
                             <span className="text-[9px] font-bold text-slate-500 tracking-widest uppercase">CONDITION</span>
                             <span className={`text-sm font-bold tracking-tight ${statusColorText}`}>
                                 {statusMsg}
                             </span>
                         </div>
                    </div>

                    {/* Divider */}
                    <div className="h-8 w-px bg-slate-700/50"></div>

                    {/* Delta Section */}
                    <div className="flex flex-col flex-1">
                         <span className="text-[9px] font-bold text-slate-500 tracking-widest uppercase">DELTA T</span>
                         <div className="flex items-baseline gap-1">
                             <span className={`text-2xl font-mono font-bold leading-none ${visualDeltaT < 2 ? 'text-slate-500' : 'text-sky-400'}`}>
                                 {system.isRunning ? visualDeltaT.toFixed(1) : '0.0'}
                             </span>
                             <span className="text-[10px] text-slate-500 font-bold">°F</span>
                         </div>
                    </div>
               </div>
           </div>

       </div>

    </div>
  );
};