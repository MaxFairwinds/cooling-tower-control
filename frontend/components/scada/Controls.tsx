import React from 'react';
import { Settings, Thermometer, Droplets, Zap } from 'lucide-react';

type PumpSelection = 'P-101' | 'OFF' | 'P-102';
type TowerSelection = 'ON' | 'OFF';

export const PumpSelector: React.FC<{ 
    x: number; 
    y: number; 
    value: PumpSelection; 
    onChange: (val: PumpSelection) => void;
    title?: string;
    isPending?: boolean;
}> = ({ x, y, value, onChange, title = "MANUAL SELECT", isPending = false }) => {
    const width = 120;
    const height = 30;
    const btnW = width / 3;
    let knobX = 0;
    if (value === 'P-101') knobX = -btnW;
    else if (value === 'P-102') knobX = btnW;
    else knobX = 0;

    return (
        <g transform={`translate(${x}, ${y})`}>
            <rect x="-60" y="-28" width="120" height="12" rx="2" fill="#0f172a" stroke="#334155" strokeWidth="1" />
            <text x="0" y="-20" textAnchor="middle" className={isPending ? "text-[8px] font-mono font-bold fill-amber-400 tracking-widest" : "text-[7px] font-mono font-bold fill-slate-400 tracking-widest"}>{isPending ? '⏳ SYNCING...' : title}</text>
            <rect x={-width/2 - 2} y={-height/2 - 2} width={width + 4} height={height + 4} rx="4" fill="#1e293b" stroke="#0f172a" strokeWidth="2" />
            <rect x={-width/2} y={-height/2} width={width} height={height} rx="2" fill="#0f172a" stroke="#334155" strokeWidth="1" />
            <g transform={`translate(${knobX}, 0)`} style={{ transition: 'transform 0.2s ease-out' }}>
                <rect x={-btnW/2 + 2} y={-height/2 + 2} width={btnW - 4} height={height - 4} rx="2" fill={value === 'OFF' ? '#334155' : '#0ea5e9'} stroke={value === 'OFF' ? '#475569' : '#38bdf8'} strokeWidth="1" className={value !== 'OFF' ? 'shadow-[0_0_10px_rgba(56,189,248,0.5)]' : ''} />
                {isPending && (
                    <>
                        <rect x={-btnW/2 + 2} y={-height/2 + 2} width={btnW - 4} height={height - 4} rx="2" fill="#fbbf24" opacity="0.7">
                            <animate attributeName="opacity" values="0.3;0.9;0.3" dur="1s" repeatCount="indefinite" />
                        </rect>
                    </>
                )}
            </g>
            <g style={{ cursor: 'pointer' }} onClick={() => onChange('P-101')}>
                <rect x={-width/2} y={-height/2} width={btnW} height={height} fill="transparent" />
                <text x={-width/3} y={4} textAnchor="middle" className="text-[9px] font-bold select-none pointer-events-none" fill={value === 'P-101' ? '#fff' : '#475569'}>101</text>
            </g>
            <g style={{ cursor: 'pointer' }} onClick={() => onChange('OFF')}>
                <rect x={-btnW/2} y={-height/2} width={btnW} height={height} fill="transparent" />
                 <text x={0} y={4} textAnchor="middle" className="text-[9px] font-bold select-none pointer-events-none" fill={value === 'OFF' ? '#fff' : '#475569'}>OFF</text>
            </g>
            <g style={{ cursor: 'pointer' }} onClick={() => onChange('P-102')}>
                <rect x={width/2 - btnW} y={-height/2} width={btnW} height={height} fill="transparent" />
                 <text x={width/3} y={4} textAnchor="middle" className="text-[9px] font-bold select-none pointer-events-none" fill={value === 'P-102' ? '#fff' : '#475569'}>102</text>
            </g>
            <circle cx={-width/3} cy={-22} r="1.5" fill={value === 'P-101' ? '#38bdf8' : '#1e293b'} />
            <circle cx={0} cy={-22} r="1.5" fill={value === 'OFF' ? '#fbbf24' : '#1e293b'} />
            <circle cx={width/3} cy={-22} r="1.5" fill={value === 'P-102' ? '#38bdf8' : '#1e293b'} />
        </g>
    );
};

export const TowerSelector: React.FC<{ 
    x: number; 
    y: number; 
    value: TowerSelection; 
    onChange: (val: TowerSelection) => void;
    title?: string;
    isPending?: boolean;
}> = ({ x, y, value, onChange, title = "TOWER SELECT", isPending = false }) => {
    const width = 120;
    const height = 30;
    const btnW = width / 2;
    let knobX = 0;
    if (value === 'ON') knobX = -btnW/2; else knobX = btnW/2;

    return (
        <g transform={`translate(${x}, ${y})`}>
            <rect x="-60" y="-28" width="120" height="12" rx="2" fill="#0f172a" stroke="#334155" strokeWidth="1" />
            <text x="0" y="-20" textAnchor="middle" className={isPending ? "text-[8px] font-mono font-bold fill-amber-400 tracking-widest" : "text-[7px] font-mono font-bold fill-slate-400 tracking-widest"}>{isPending ? '⏳ SYNCING...' : title}</text>
            <rect x={-width/2 - 2} y={-height/2 - 2} width={width + 4} height={height + 4} rx="4" fill="#1e293b" stroke="#0f172a" strokeWidth="2" />
            <rect x={-width/2} y={-height/2} width={width} height={height} rx="2" fill="#0f172a" stroke="#334155" strokeWidth="1" />
            <g transform={`translate(${knobX}, 0)`} style={{ transition: 'transform 0.2s ease-out' }}>
                <rect x={-btnW/2 + 2} y={-height/2 + 2} width={btnW - 4} height={height - 4} rx="2" fill={value === 'OFF' ? '#334155' : '#0ea5e9'} stroke={value === 'OFF' ? '#475569' : '#38bdf8'} strokeWidth="1" className={value !== 'OFF' ? 'shadow-[0_0_10px_rgba(56,189,248,0.5)]' : ''} />                {isPending && (
                    <>
                        <rect x={-btnW/2 + 2} y={-height/2 + 2} width={btnW - 4} height={height - 4} rx="2" fill="#fbbf24" opacity="0.7">
                            <animate attributeName="opacity" values="0.3;0.9;0.3" dur="1s" repeatCount="indefinite" />
                        </rect>
                    </>
                )}            </g>
            <g style={{ cursor: 'pointer' }} onClick={() => onChange('ON')}>
                <rect x={-width/2} y={-height/2} width={btnW} height={height} fill="transparent" />
                <text x={-width/2 + btnW/2} y={4} textAnchor="middle" className="text-[9px] font-bold select-none pointer-events-none" fill={value === 'ON' ? '#fff' : '#475569'}>ON</text>
            </g>
            <g style={{ cursor: 'pointer' }} onClick={() => onChange('OFF')}>
                <rect x={0} y={-height/2} width={btnW} height={height} fill="transparent" />
                 <text x={btnW/2} y={4} textAnchor="middle" className="text-[9px] font-bold select-none pointer-events-none" fill={value === 'OFF' ? '#fff' : '#475569'}>OFF</text>
            </g>
            <circle cx={-width/4} cy={-22} r="1.5" fill={value === 'ON' ? '#38bdf8' : '#1e293b'} />
            <circle cx={width/4} cy={-22} r="1.5" fill={value === 'OFF' ? '#fbbf24' : '#1e293b'} />
        </g>
    );
};

// --- NEW COMPONENTS ---

export const FanController: React.FC<{
    x: number;
    y: number;
    manualMode: boolean;
    frequency: number;
    setpoint: number;
    onToggleMode: () => void;
    onSetHz: (hz: number) => void;
    enabled: boolean;
}> = ({ x, y, manualMode, frequency, setpoint, onToggleMode, onSetHz, enabled }) => {
    // A small VFD panel drawn in SVG
    if (!enabled) return null;

    const width = 100;
    const height = 50;

    return (
        <g transform={`translate(${x}, ${y})`}>
            {/* Connector Line to Tower Selector */}
            <line x1="-70" y1="0" x2="-50" y2="0" stroke="#334155" strokeWidth="1" strokeDasharray="2 2" />

            {/* Panel Body */}
            <rect x={-width/2} y={-height/2} width={width} height={height} rx="4" fill="#0f172a" stroke="#334155" strokeWidth="1" />
            
            {/* Header */}
            <rect x={-width/2} y={-height/2} width={width} height={14} rx="4" fill="#1e293b" />
            <text x={0} y={-height/2 + 10} textAnchor="middle" className="text-[8px] font-bold fill-slate-300 tracking-wider">FAN VFD CONTROL</text>

            {/* Mode Switch (Clickable) */}
            <g transform="translate(-30, 0)" onClick={onToggleMode} style={{ cursor: 'pointer' }}>
                <rect x="-15" y="-6" width="30" height="12" rx="2" fill="#334155" stroke="#475569" strokeWidth="0.5" />
                <text x="0" y="2.5" textAnchor="middle" className="text-[7px] font-mono font-bold fill-white">
                    {manualMode ? "MAN" : "AUTO"}
                </text>
                <rect x="-15" y="-6" width="30" height="12" rx="2" fill="transparent" /> {/* Hitbox */}
            </g>

            {/* Manual Slider / Auto Display */}
            <g transform="translate(15, 0)">
                {manualMode ? (
                    // Simple SVG Slider Representation
                    <g>
                        {/* Track */}
                        <line x1="-25" y1="0" x2="25" y2="0" stroke="#475569" strokeWidth="2" strokeLinecap="round" />
                        {/* Thumb */}
                        <circle 
                            cx={-25 + (setpoint / 60) * 50} 
                            cy="0" 
                            r="5" 
                            fill="#38bdf8" 
                            stroke="#fff" 
                            strokeWidth="1"
                            style={{ cursor: 'col-resize' }}
                            // Note: Real dragging in SVG requires complex state/event handlers. 
                            // For this "widget" simulation, we act as buttons or simple step interactions
                        />
                        {/* Interaction Areas (Stepped) */}
                        {[0, 10, 20, 30, 40, 50, 60].map(val => (
                             <rect 
                                key={val}
                                x={-25 + (val / 60) * 50 - 3}
                                y="-6"
                                width="6"
                                height="12"
                                fill="transparent"
                                style={{ cursor: 'pointer' }}
                                onClick={() => onSetHz(val)}
                             />
                        ))}
                    </g>
                ) : (
                    // Auto Display
                    <text x="0" y="2.5" textAnchor="middle" className="text-[9px] font-mono font-bold fill-emerald-400">
                        {frequency.toFixed(1)} Hz
                    </text>
                )}
            </g>

            {/* Hz Label */}
            <text x="15" y="15" textAnchor="middle" className="text-[7px] font-mono fill-slate-500">
                {manualMode ? `${setpoint.toFixed(0)} Hz` : "PID ACTIVE"}
            </text>
        </g>
    );
};

export const AirTempWidget: React.FC<{
    value: number;
    onChange: (val: number) => void;
}> = ({ value, onChange }) => {
    return (
        <div className="flex items-center gap-2 bg-slate-800/50 rounded px-2 py-1 border border-slate-700 shadow-sm">
            <div className="text-slate-400">
                <Thermometer size={14} />
            </div>
            <div className="flex flex-col">
                <span className="text-[8px] text-slate-500 font-bold uppercase leading-none">Outdoor Air</span>
                <span className="text-xs font-mono font-bold text-amber-400 leading-none">{value.toFixed(1)}°F</span>
            </div>
            <div className="flex flex-col gap-0.5 ml-1">
                <button 
                    onClick={() => onChange(Math.min(value + 1.0, 115))}
                    className="w-4 h-3 bg-slate-700 hover:bg-slate-600 rounded-sm flex items-center justify-center text-[8px] text-white"
                >
                    +
                </button>
                <button 
                    onClick={() => onChange(Math.max(value - 1.0, 32))}
                    className="w-4 h-3 bg-slate-700 hover:bg-slate-600 rounded-sm flex items-center justify-center text-[8px] text-white"
                >
                    -
                </button>
            </div>
        </div>
    );
};

export const HumidityWidget: React.FC<{
    value: number;
    onChange: (val: number) => void;
}> = ({ value, onChange }) => {
    return (
        <div className="flex items-center gap-2 bg-slate-800/50 rounded px-2 py-1 border border-slate-700 shadow-sm">
            <div className="text-slate-400">
                <Droplets size={14} />
            </div>
            <div className="flex flex-col">
                <span className="text-[8px] text-slate-500 font-bold uppercase leading-none">Humidity</span>
                <span className="text-xs font-mono font-bold text-sky-400 leading-none">{value.toFixed(0)}%</span>
            </div>
            <div className="flex flex-col gap-0.5 ml-1">
                <button 
                    onClick={() => onChange(Math.min(value + 5.0, 100))}
                    className="w-4 h-3 bg-slate-700 hover:bg-slate-600 rounded-sm flex items-center justify-center text-[8px] text-white"
                >
                    +
                </button>
                <button 
                    onClick={() => onChange(Math.max(value - 5.0, 0))}
                    className="w-4 h-3 bg-slate-700 hover:bg-slate-600 rounded-sm flex items-center justify-center text-[8px] text-white"
                >
                    -
                </button>
            </div>
        </div>
    );
};

export const HeatLoadWidget: React.FC<{
    value: number;
    onChange: (val: number) => void;
}> = ({ value, onChange }) => {
    return (
        <div className="flex items-center gap-2 bg-slate-800/50 rounded px-2 py-1 border border-slate-700 shadow-sm">
            <div className="text-slate-400">
                <Zap size={14} />
            </div>
            <div className="flex flex-col">
                <span className="text-[8px] text-slate-500 font-bold uppercase leading-none">Load Sim</span>
                <span className="text-xs font-mono font-bold text-rose-400 leading-none">{value.toFixed(0)}%</span>
            </div>
            <div className="flex flex-col gap-0.5 ml-1">
                <button 
                    onClick={() => onChange(Math.min(value + 10, 100))}
                    className="w-4 h-3 bg-slate-700 hover:bg-slate-600 rounded-sm flex items-center justify-center text-[8px] text-white"
                >
                    +
                </button>
                <button 
                    onClick={() => onChange(Math.max(value - 10, 0))}
                    className="w-4 h-3 bg-slate-700 hover:bg-slate-600 rounded-sm flex items-center justify-center text-[8px] text-white"
                >
                    -
                </button>
            </div>
        </div>
    );
};