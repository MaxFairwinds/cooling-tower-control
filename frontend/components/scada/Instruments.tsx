import React from 'react';

// Reusable defs for gradients (can be placed in each component or a shared provider, placing inside for isolation)
const InstrumentDefs = ({ id }: { id: string }) => (
    <defs>
        <linearGradient id={`${id}-coupling-metal`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#334155" />
            <stop offset="50%" stopColor="#94a3b8" />
            <stop offset="100%" stopColor="#334155" />
        </linearGradient>
        <filter id={`${id}-drop-shadow`}>
            <feDropShadow dx="1" dy="2" stdDeviation="2" floodOpacity="0.3" />
        </filter>
        <radialGradient id={`${id}-face-shine`} cx="0.3" cy="0.3" r="0.7">
             <stop offset="0%" stopColor="#ffffff" stopOpacity="0.8" />
             <stop offset="100%" stopColor="#ffffff" stopOpacity="0" />
        </radialGradient>
        {/* Glass Screen Reflection Gradient */}
        <linearGradient id={`${id}-glass-glare`} x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="white" stopOpacity="0.15" />
            <stop offset="40%" stopColor="white" stopOpacity="0.05" />
            <stop offset="100%" stopColor="white" stopOpacity="0" />
        </linearGradient>
    </defs>
);

// New Realistic Saddle Coupling (Wraps the pipe)
const InstrumentCoupling: React.FC<{ id: string }> = ({ id }) => (
    <g>
        {/* Back Strap (Bottom of pipe) */}
        <path d="M -14 6 Q 0 10 14 6 L 14 14 Q 0 18 -14 14 Z" fill="#1e293b" stroke="#0f172a" strokeWidth="1" />
        
        {/* Front Strap (Top of pipe - Saddle) */}
        <path 
            d="M -16 -10 Q 0 -14 16 -10 L 16 8 Q 0 4 -16 8 Z" 
            fill={`url(#${id}-coupling-metal)`} 
            stroke="#0f172a" 
            strokeWidth="1"
        />
        
        {/* Bubble Sight Glass Window */}
        <g transform="translate(0, -3)">
             {/* Metal Bezel */}
             <circle r="5" fill="#475569" stroke="#0f172a" strokeWidth="0.5" />
             {/* Glass Interior */}
             <circle r="3.5" fill="#020617" stroke="#0f172a" strokeWidth="0.5" />
             <circle r="3.5" fill="#38bdf8" fillOpacity="0.2" />
             {/* Highlight */}
             <path d="M -2 -2 Q 0 -3 2 -2" stroke="white" strokeWidth="1" strokeLinecap="round" opacity="0.6" fill="none" />
             <circle cx="1.5" cy="1.5" r="0.5" fill="white" opacity="0.4" />
        </g>
        
        {/* Side Bolts/Tensioners */}
        <g transform="translate(-16, -2)">
            <rect x="-2" y="-4" width="4" height="8" rx="1" fill="#475569" stroke="#0f172a" strokeWidth="0.5" />
            <line x1="0" y1="-3" x2="0" y2="3" stroke="#1e293b" strokeWidth="0.5" />
        </g>
        <g transform="translate(16, -2)">
            <rect x="-2" y="-4" width="4" height="8" rx="1" fill="#475569" stroke="#0f172a" strokeWidth="0.5" />
            <line x1="0" y1="-3" x2="0" y2="3" stroke="#1e293b" strokeWidth="0.5" />
        </g>
        
        {/* Vertical Stem (Thermowell / Tap) */}
        <rect x="-6" y="-22" width="12" height="14" fill="#334155" stroke="#0f172a" strokeWidth="1" />
        {/* Hex Nut at base of stem */}
        <path d="M -8 -12 L -4 -8 L 4 -8 L 8 -12 L 4 -16 L -4 -16 Z" fill="#475569" stroke="#0f172a" strokeWidth="0.5" />
    </g>
);

export const InlineDigitalGauge: React.FC<{
    x: number;
    y: number;
    value: number;
    label: string;
    unit?: string;
    color?: string;
}> = ({ x, y, value, label, unit = "°F", color = "#38bdf8" }) => {
    const id = `digi-gauge-${x}-${y}`;

    return (
        <g transform={`translate(${x}, ${y})`}>
            <InstrumentDefs id={id} />
            
            {/* New Improved Coupling */}
            <InstrumentCoupling id={id} />

            {/* --- DISPLAY UNIT (Mounted Above) --- */}
            <g transform="translate(0, -22)" filter={`url(#${id}-drop-shadow)`}>
                {/* Stem / Neck Connection */}
                <rect x="-3" y="-8" width="6" height="8" fill="#1e293b" />

                {/* Main Head Housing */}
                <g transform="translate(0, -26)">
                    {/* Housing Body */}
                    <rect x="-32" y="-12" width="64" height="34" rx="3" fill="#1e293b" stroke="#475569" strokeWidth="1.5" />
                    
                    {/* Screen Bezel */}
                    <rect x="-28" y="-8" width="56" height="20" rx="1" fill="#020617" stroke="#0f172a" strokeWidth="1" />
                    
                    {/* LCD Screen Background */}
                    <linearGradient id={`${id}-screen-grad`} x1="0" y1="0" x2="0" y2="1">
                         <stop offset="0%" stopColor="#0f172a" />
                         <stop offset="100%" stopColor="#1e293b" />
                    </linearGradient>
                    <rect x="-26" y="-6" width="52" height="16" fill={`url(#${id}-screen-grad)`} />
                    
                    {/* Digital Value */}
                    <text 
                        x="0" 
                        y="5" 
                        textAnchor="middle" 
                        className="text-[14px] font-mono font-bold tracking-tight"
                        fill={color}
                        style={{ textShadow: `0 0 5px ${color}` }}
                    >
                        {value.toFixed(1)}
                    </text>
                    
                    {/* Unit Label */}
                    <text x="22" y="5" textAnchor="end" className="text-[6px] font-mono fill-slate-500 font-bold">{unit}</text>

                    {/* --- GLASS WINDOW EFFECT --- */}
                    {/* Top Glare */}
                    <path d="M -26 -6 L 26 -6 L 26 2 L -26 -2 Z" fill="white" opacity="0.1" />
                    {/* Diagonal Reflection */}
                    <rect x="-26" y="-6" width="52" height="16" fill={`url(#${id}-glass-glare)`} pointerEvents="none" />
                    {/* Hard Highlight Edge */}
                    <path d="M -25 -5 L -10 -5" stroke="white" strokeWidth="1" opacity="0.2" strokeLinecap="round" />

                    {/* Label Plate */}
                    <rect x="-20" y="14" width="40" height="6" rx="1" fill="#334155" />
                    <text x="0" y="19" textAnchor="middle" className="text-[4px] font-bold fill-white tracking-widest uppercase">
                        {label}
                    </text>
                </g>
            </g>
        </g>
    );
};

export const AnalogPressureGauge: React.FC<{
    x: number;
    y: number;
    value: number;
    label?: string;
    min?: number;
    max?: number;
}> = ({ x, y, value, label="PSI", min=0, max=100 }) => {
    const id = `ana-gauge-${x}-${y}`;
    
    // Clamp value
    const clampedVal = Math.max(min, Math.min(max, value));
    const percent = (clampedVal - min) / (max - min);
    // Range: -135deg to +135deg (Total 270deg sweep)
    const angle = -135 + (percent * 270);

    return (
        <g transform={`translate(${x}, ${y})`}>
            <InstrumentDefs id={id} />
            <InstrumentCoupling id={id} />

            {/* Gauge Head */}
            <g transform="translate(0, -48)" filter={`url(#${id}-drop-shadow)`}>
                {/* Stem */}
                <rect x="-4" y="20" width="8" height="14" fill="#94a3b8" stroke="#0f172a" strokeWidth="0.5" />
                <path d="M -5 26 L 5 26 L 5 30 L -5 30 Z" fill="#64748b" stroke="#0f172a" strokeWidth="0.5" /> {/* Coupling nut */}
                
                {/* Outer Casing (Chrome) */}
                <circle r="28" fill="#e2e8f0" stroke="#475569" strokeWidth="4" />
                <circle r="28" fill="none" stroke="#0f172a" strokeWidth="0.5" opacity="0.5" />
                <circle r="26" fill="none" stroke="#fff" strokeWidth="1" opacity="0.6" />
                
                {/* Inner Face */}
                <circle r="24" fill="#f8fafc" stroke="#94a3b8" strokeWidth="0.5" />
                
                {/* Ticks */}
                {[...Array(11)].map((_, i) => {
                    const tickAngle = -135 + (i * 27) - 90; // SVG rotation is clockwise from 3 o'clock
                    return (
                        <g key={i} transform={`rotate(${tickAngle})`}>
                            <line x1="18" y1="0" x2="22" y2="0" stroke="#334155" strokeWidth={i % 5 === 0 ? 1.5 : 0.5} />
                        </g>
                    )
                })}

                {/* Safe/Danger Zones on Face */}
                {/* Green Arc (Normal: 30-70%) */}
                <path d="M -12 -12 A 17 17 0 0 1 12 -12" fill="none" stroke="#10b981" strokeWidth="2" strokeLinecap="round" opacity="0.2" transform="rotate(180)" />
                {/* Red Arc (High: >90%) */}
                <path d="M 12 12 A 17 17 0 0 0 20 5" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round" opacity="0.4" />
                
                {/* Numeric Readout Box (New & Enlarged) */}
                <rect x="-11" y="14" width="22" height="9" rx="1" fill="#e2e8f0" stroke="#cbd5e1" strokeWidth="0.5" />
                <text x="0" y="21" textAnchor="middle" className="text-[8px] font-mono font-black fill-slate-800 tracking-tight">
                    {value.toFixed(0)}
                </text>

                {/* Label (Enlarged) */}
                <text x="0" y="10" textAnchor="middle" className="text-[7px] font-black fill-slate-400 font-sans tracking-widest">{label}</text>
                
                {/* Needle */}
                <g transform={`rotate(${angle})`} style={{ transition: 'transform 0.5s cubic-bezier(0.4, 0, 0.2, 1)' }}>
                    <path d="M -2 0 L 0 -22 L 2 0 L 0 5 Z" fill="#dc2626" stroke="#991b1b" strokeWidth="0.5" />
                    <circle r="2.5" fill="#1e293b" stroke="#0f172a" strokeWidth="0.5" />
                    <circle r="1" fill="#475569" />
                </g>
                
                {/* Convex Glass Reflection */}
                <path d="M -18 -12 Q 0 -24 18 -12" fill="none" stroke="white" strokeWidth="3" opacity="0.3" strokeLinecap="round" />
                <circle r="24" fill={`url(#${id}-face-shine)`} opacity="0.3" pointerEvents="none" />
            </g>
        </g>
    );
};