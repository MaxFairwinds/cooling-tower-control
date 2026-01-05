import React from 'react';

// --- HORIZONTAL MOTOR INLINE PUMP COMPONENT ---
// Rotated motor to allow tight vertical stacking
export const InlinePump: React.FC<{ x: number; y: number; status: 'Running' | 'Stopped' | 'Fault'; label: string; freq: number }> = ({ x, y, status, label, freq }) => {
    const isRunning = status === 'Running';
    const isFault = status === 'Fault';
    const accentColor = isRunning ? "#10b981" : isFault ? "#f43f5e" : "#64748b";
    const id = `pump-${x}-${y}`;

    return (
        <g transform={`translate(${x}, ${y})`}>
            <defs>
                <linearGradient id={`${id}-body-grad-horiz`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#0f172a" />
                    <stop offset="20%" stopColor="#334155" />
                    <stop offset="50%" stopColor="#475569" />
                    <stop offset="80%" stopColor="#334155" />
                    <stop offset="100%" stopColor="#0f172a" />
                </linearGradient>

                <linearGradient id={`${id}-cast-iron`} x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stopColor="#1e293b" />
                    <stop offset="50%" stopColor="#334155" />
                    <stop offset="100%" stopColor="#0f172a" />
                </linearGradient>

                {/* Intense Green Glow Filter - Applied ONLY to the status strip */}
                <filter id={`${id}-run-glow`} x="-50%" y="-50%" width="200%" height="200%">
                    <feGaussianBlur in="SourceAlpha" stdDeviation="1" result="blur"/>
                    <feFlood floodColor="#10b981" floodOpacity="0.9" result="color"/>
                    <feComposite in="color" in2="blur" operator="in" result="coloredBlur"/>
                    <feMerge>
                        <feMergeNode in="coloredBlur"/>
                        <feMergeNode in="SourceGraphic"/>
                    </feMerge>
                </filter>
            </defs>

            {/* 1. MOTOR ASSEMBLY (Rendered BEHIND pipes for "Inline" effect) */}
            {/* Extending to the RIGHT (+X) */}
            <g transform="translate(15, 0)"> 
                {/* Motor Neck/Coupling */}
                <path d="M 0 -15 L 25 -20 L 25 20 L 0 15 Z" fill="url(#industrial-metal)" stroke="#0f172a" />
                
                {/* Shaft Window / Coupling Guard */}
                <rect x="5" y="-8" width="15" height="16" fill="#000" opacity="0.4" rx="2" />
                {/* Safety Mesh */}
                <path d="M 5 -8 L 20 8 M 5 -4 L 20 12 M 5 0 L 20 16" stroke="#fff" strokeWidth="0.5" opacity="0.2" />
                <path d="M 20 -8 L 5 8 M 20 -4 L 5 12 M 20 0 L 5 16" stroke="#fff" strokeWidth="0.5" opacity="0.2" />

                {isRunning && (
                    <rect x="7" y="-6" width="11" height="12" fill="url(#fan-blade-composite)" opacity="0.5" className="animate-spin-linear" style={{ transformBox: 'fill-box', transformOrigin: 'center' }} />
                )}

                {/* Main Motor Housing (Horizontal Cylinder) */}
                <g transform="translate(25, 0)">
                    {/* Body - NO GREEN STROKE HERE, just standard border */}
                    <rect 
                        x="0" y="-35" width="80" height="70" rx="2" 
                        fill={`url(#${id}-body-grad-horiz)`} 
                        stroke="#0f172a" 
                        strokeWidth="2"
                    />
                    
                    {/* Status Indicator Strip (Integrated onto motor body) - GLOW APPLIED HERE */}
                    <rect 
                        x="6" y="-35" width="6" height="70" 
                        fill={isRunning ? accentColor : "#1e293b"} 
                        opacity={isRunning ? 1 : 0.5}
                        filter={isRunning ? `url(#${id}-run-glow)` : undefined}
                    >
                         {isRunning && <animate attributeName="opacity" values="0.8;1;0.8" dur="1s" repeatCount="indefinite" />}
                    </rect>
                    <line x1="12" y1="-35" x2="12" y2="35" stroke="#0f172a" strokeWidth="1" opacity="0.5" />

                    {/* Cooling Fins (Horizontal now) */}
                    {[-20, -10, 0, 10, 20].map(posY => (
                        <line key={posY} x1="18" y1={posY} x2="75" y2={posY} stroke="#000" strokeOpacity="0.3" strokeWidth="1" />
                    ))}

                    {/* End Fan Cap */}
                    <path d="M 80 -35 C 90 -35, 90 35, 80 35" fill="#334155" stroke="#0f172a" />
                    <line x1="88" y1="-10" x2="88" y2="10" stroke="#0f172a" opacity="0.5" />

                    {/* Terminal Box (Top) */}
                    <g transform="translate(30, -45)">
                        <rect x="0" y="0" width="24" height="14" fill="#475569" stroke="#0f172a" rx="1"/>
                        {/* Power LED */}
                        <circle cx="12" cy="0" r="3" fill="#1e293b" stroke="#0f172a" strokeWidth="1" />
                        <circle cx="12" cy="0" r="2" fill={accentColor} className={isRunning ? "animate-pulse" : ""} opacity={isRunning ? 1 : 0.3} />
                    </g>

                    {/* Digital Interface (Side/Front Face) */}
                    <g transform="translate(25, 15)">
                        <rect x="0" y="0" width="28" height="14" fill="#000" stroke={isRunning ? accentColor : "#475569"} strokeWidth={isRunning ? 1 : 0.5} rx="1" />
                        {isRunning ? (
                             <text x="14" y="10" textAnchor="middle" className="text-[8px] font-mono fill-white" style={{ fontFamily: 'monospace' }}>{freq.toFixed(0)}Hz</text>
                        ) : (
                             <text x="14" y="10" textAnchor="middle" className="text-[8px] font-mono fill-gray-600">OFF</text>
                        )}
                    </g>
                </g>
            </g>

            {/* 2. VOLUTE (Wet End) - High Detail Cast Iron Look */}
            <g>
                 {/* Flanges (Connection to Pipe) */}
                 {/* Left */}
                 <path d="M -30 -14 L -24 -14 L -24 14 L -30 14 Z" fill="#334155" stroke="#0f172a" />
                 {/* Right */}
                 <path d="M 30 -14 L 24 -14 L 24 14 L 30 14 Z" fill="#334155" stroke="#0f172a" />
                 
                 {/* Main Casing Body - Bulbous Cast Iron shape */}
                 <circle cx="0" cy="0" r="22" fill={`url(#${id}-cast-iron)`} stroke="#0f172a" strokeWidth="1.5" />
                 
                 {/* Front Seal Plate / Cover */}
                 <circle cx="0" cy="0" r="14" fill="#1e293b" stroke="#0f172a" strokeWidth="1" />
                 <circle cx="0" cy="0" r="6" fill="#0f172a" stroke="#334155" strokeWidth="0.5" />
                 
                 {/* Bolt Circle on Front Plate */}
                 {[0, 45, 90, 135, 180, 225, 270, 315].map(deg => (
                     <circle key={deg} cx={11 * Math.cos(deg*Math.PI/180)} cy={11 * Math.sin(deg*Math.PI/180)} r="1.2" fill="#64748b" stroke="#0f172a" strokeWidth="0.5" />
                 ))}
                 
                 {/* Structural Ribs */}
                 <path d="M -22 0 L -14 0" stroke="#0f172a" strokeWidth="1" opacity="0.5" />
                 <path d="M 14 0 L 22 0" stroke="#0f172a" strokeWidth="1" opacity="0.5" />
                 <path d="M 0 -22 L 0 -14" stroke="#0f172a" strokeWidth="1" opacity="0.5" />
                 <path d="M 0 14 L 0 22" stroke="#0f172a" strokeWidth="1" opacity="0.5" />
            </g>
            
            {/* 4. Base Support (Simple bracket under volute) */}
            <g transform="translate(0, 25)">
                <path d="M -5 -10 L -5 10 L 5 10 L 5 -10 Z" fill="#334155" stroke="#0f172a" />
                <rect x="-15" y="10" width="30" height="4" fill="#1e293b" stroke="#0f172a" />
            </g>

            {/* Label */}
            <g transform="translate(60, 55)">
                <rect x="-35" y="-8" width="70" height="14" rx="2" fill="#0f172a" stroke="#334155" />
                <text x="0" y="2" textAnchor="middle" className="text-[8px] font-mono font-bold fill-white tracking-widest">{label}</text>
            </g>

        </g>
    );
};