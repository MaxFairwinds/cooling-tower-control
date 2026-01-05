import React from 'react';

// Water Source Heat Pump (WSHP) Graphic - Closed Panel
export const WSHP: React.FC<{ 
    x: number; 
    y: number; 
    isRunning: boolean; 
    enteringWaterTemp: number;
    dischargeAirTemp: number;
}> = ({ x, y, isRunning, enteringWaterTemp, dischargeAirTemp }) => {
    const id = `wshp-${x}-${y}`;
    
    // Safety Logic: Compressor trips if water > 104F (Unit typically designed for <95-100)
    // We infer compressor status from the air temp. If Air is cold (<70) & system running, compressor is ON.
    const isCompressorOn = isRunning && dischargeAirTemp < 70;
    const isTrip = isRunning && !isCompressorOn;

    // Helper to color code air temp based on efficiency status
    const getAirColor = (t: number) => {
        if (!isRunning || isTrip) return 'fill-slate-600'; // Off or Tripped
        if (t < 58) return 'fill-cyan-400'; // Optimal (Green Zone)
        if (t < 70) return 'fill-amber-400'; // Struggling (Yellow Zone)
        return 'fill-slate-600'; // Should theoretically be caught by isTrip, but safe fallback
    };

    return (
        <g transform={`translate(${x}, ${y})`}>
            <defs>
                {/* Metallic Cabinet - Darker Slate */}
                <linearGradient id={`${id}-cabinet`} x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="#1e293b" /> 
                    <stop offset="15%" stopColor="#334155" />
                    <stop offset="40%" stopColor="#475569" />
                    <stop offset="60%" stopColor="#334155" />
                    <stop offset="100%" stopColor="#0f172a" />
                </linearGradient>

                {/* Mesh Pattern for Fan */}
                <pattern id={`${id}-mesh`} width="4" height="4" patternUnits="userSpaceOnUse">
                    <circle cx="2" cy="2" r="1" fill="#000" opacity="0.6"/>
                </pattern>
                
                {/* Fan Blade Gradient */}
                <linearGradient id={`${id}-blade`} x1="0" y1="0" x2="1" y2="1">
                     <stop offset="0%" stopColor="#1e293b" />
                     <stop offset="50%" stopColor="#475569" />
                     <stop offset="100%" stopColor="#0f172a" />
                </linearGradient>

                 {/* LCD Glow */}
                <filter id={`${id}-lcd-glow`}>
                    <feGaussianBlur stdDeviation="1.0" result="coloredBlur"/>
                    <feMerge>
                        <feMergeNode in="coloredBlur"/>
                        <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                </filter>
            </defs>

            {/* --- MAIN CABINET FRAME --- */}
            {/* Outer Shell */}
            <rect x="-75" y="-140" width="150" height="235" rx="4" fill={`url(#${id}-cabinet)`} stroke="#0f172a" strokeWidth="2" />
            
            {/* Top Cap (Fan Deck) */}
            <path d="M -75 -140 L 75 -140 L 75 -90 L -75 -90 Z" fill="#0f172a" opacity="0.4" />

            {/* Side Vents - Louver style */}
            {[...Array(20)].map((_, i) => (
                <path key={i} d={`M -70 ${-120 + i*5} L -30 ${-120 + i*5}`} stroke="#020617" strokeWidth="2" strokeOpacity="0.5" strokeLinecap="round" />
            ))}
             {[...Array(20)].map((_, i) => (
                <path key={i} d={`M 30 ${-120 + i*5} L 70 ${-120 + i*5}`} stroke="#020617" strokeWidth="2" strokeOpacity="0.5" strokeLinecap="round" />
            ))}

            {/* --- AIR DISCHARGE VENT (Left Side) --- */}
            <g transform="translate(-75, -60)">
                {/* REMOVED Duct Collar and Airflow Arrows as requested */}
            </g>

            {/* --- ACCESS PANEL (Bottom) --- */}
            <g transform="translate(0, 15)">
                {/* Panel Bevel */}
                <rect x="-65" y="-65" width="130" height="150" rx="1" fill="none" stroke="#475569" strokeWidth="1" strokeOpacity="0.3" />
                <rect x="-64" y="-64" width="128" height="148" rx="1" fill="none" stroke="#0f172a" strokeWidth="1" strokeOpacity="0.8" />
                
                {/* Handle */}
                <rect x="-10" y="-15" width="20" height="6" rx="2" fill="#0f172a" />
                
                {/* Branding/Stickers */}
                <rect x="-20" y="60" width="40" height="12" fill="#334155" opacity="0.5" />
            </g>

            {/* --- PIPING STUBS --- */}
             {/* Top Return Stub (Vertical into top CENTER) */}
             <path d="M 0 -140 L 0 -120" stroke="#334155" strokeWidth="6" />
             {/* Bottom Supply Stub (Extended Left) */}
             <path d="M -74 40 L -55 40" stroke="#334155" strokeWidth="6" />

            {/* --- DUAL INDICATOR HMI (Status Display) --- */}
            <g transform="translate(0, -20)">
                {/* Bezel - Tall for 2 rows */}
                <rect x="-38" y="-22" width="76" height="44" rx="3" fill="#1e293b" stroke="#475569" strokeWidth="2" />
                
                {/* Screen Area */}
                <rect x="-34" y="-18" width="68" height="36" fill="#000" />
                
                {/* Digital Readout Group */}
                <g filter={`url(#${id}-lcd-glow)`}>
                     {/* Label Centered at Top */}
                     <text x="0" y="-10" textAnchor="middle" className="text-[6px] font-mono fill-slate-500 font-bold tracking-tight">LAT (AIR)</text>
                     
                     {/* Value - ENLARGED and Centered */}
                     <text x="0" y="6" textAnchor="middle" className={`text-[16px] font-mono font-bold tracking-tighter ${getAirColor(dischargeAirTemp)}`}>
                        {dischargeAirTemp.toFixed(1)}°
                    </text>
                    
                    <line x1="-32" y1="10" x2="32" y2="10" stroke="#334155" strokeWidth="0.5" />
                    
                    {/* Status Text */}
                    <text x="0" y="15" textAnchor="middle" className={`text-[6px] font-bold tracking-widest ${isTrip ? 'fill-rose-500' : isCompressorOn ? 'fill-emerald-500' : 'fill-slate-600'}`}>
                        {isTrip ? "HIGH TEMP TRIP" : isCompressorOn ? "COMPRESSOR ON" : "STANDBY"}
                    </text>
                </g>
                
                {/* LED Indicators on bezel */}
                {/* Power */}
                <circle cx="-42" cy="-12" r="1.5" fill={isRunning ? "#10b981" : "#334155"} />
                {/* Alarm */}
                <circle cx="-42" cy="12" r="1.5" fill={isTrip ? "#ef4444" : "#334155"} className={isTrip ? "animate-pulse" : ""} />
                
                {/* Screen Reflection Gloss */}
                <path d="M -34 -18 L 34 -18 L 34 -5 L -34 -12 Z" fill="#fff" opacity="0.05" />
            </g>

            {/* LABEL */}
             <g transform="translate(0, 110)">
                <rect x="-40" y="-8" width="80" height="16" fill="#0f172a" rx="2" stroke="#334155" />
                <text x="0" y="3" textAnchor="middle" className="text-[9px] font-mono font-bold fill-white tracking-widest">5913 Load</text>
            </g>

            {/* --- FAN SECTION (Top) --- */}
            <g transform="translate(0, -100)">
                {/* Fan Shroud Depression - Deeper look */}
                <circle cx="0" cy="0" r="38" fill="#020617" opacity="0.6" />
                <circle cx="0" cy="0" r="36" fill="none" stroke="#1e293b" strokeWidth="2" />
                
                {/* Inner motor mounting circle */}
                <circle cx="0" cy="0" r="10" fill="none" stroke="#1e293b" strokeWidth="2" opacity="0.5" />

                {/* IMPROVED FAN BLADES - High Fidelity Swept Aerofoil */}
                <g className={isRunning ? "animate-spin-slow" : ""} style={{ animationDuration: '0.5s' }}>
                    {[0, 72, 144, 216, 288].map((angle) => (
                        <g key={angle} transform={`rotate(${angle})`}>
                            {/* Aerodynamic Swept Blade */}
                            <path 
                                d="M 0 0 C 5 10 15 20 12 34 C 5 36 -5 36 -12 34 C -15 20 -5 10 0 0" 
                                fill={`url(#${id}-blade)`} 
                                stroke="#000"
                                strokeWidth="0.5"
                            />
                            {/* Blade Rib/Contour Line */}
                            <path d="M 0 5 Q 0 20 -4 30" stroke="#fff" strokeOpacity="0.1" fill="none" />
                        </g>
                    ))}
                    
                    {/* Detailed Hub Cap */}
                    <circle cx="0" cy="0" r="9" fill="#1e293b" stroke="#0f172a" />
                    <circle cx="0" cy="0" r="5" fill="#334155" stroke="#0f172a" strokeWidth="0.5" />
                    <circle cx="0" cy="0" r="2" fill="#0f172a" />
                    {/* Hub Bolts */}
                    {[0, 90, 180, 270].map(a => (
                        <circle key={a} cx={7 * Math.cos(a*Math.PI/180)} cy={7 * Math.sin(a*Math.PI/180)} r="0.8" fill="#64748b" />
                    ))}
                </g>
                
                {/* IMPROVED WIRE GUARD - Realistic Spiral Grill */}
                <g pointerEvents="none">
                     {/* Mounting Arms (4-point spider) */}
                     <path d="M -36 0 L -10 0 M 36 0 L 10 0 M 0 -36 L 0 -10 M 0 36 L 0 10" stroke="#0f172a" strokeWidth="2" strokeLinecap="round" />
                     
                     {/* Wire Rings */}
                     {[14, 20, 26, 32].map(r => (
                         <circle key={r} cx="0" cy="0" r={r} fill="none" stroke="#1e293b" strokeWidth="1" />
                     ))}
                     
                     {/* Highlights on wire rings for metallic look */}
                     {[14, 20, 26, 32].map(r => (
                         <path key={`hl-${r}`} d={`M ${r * Math.cos(-45*Math.PI/180)} ${r * Math.sin(-45*Math.PI/180)} A ${r} ${r} 0 0 1 ${r * Math.cos(0)} ${r * Math.sin(0)}`} stroke="#475569" strokeWidth="1" fill="none" />
                     ))}
                </g>
            </g>
        </g>
    );
};