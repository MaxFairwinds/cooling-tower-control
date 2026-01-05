import React from 'react';

// Layer 1 & 2: Structure
export const PipeStructure: React.FC<{ d: string; width?: number }> = ({ d, width = 12 }) => (
    <g>
        {/* 1. Pipe Casing (Dark Outer Border) */}
        <path d={d} fill="none" stroke="#0f172a" strokeWidth={width + 4} strokeLinecap="round" strokeLinejoin="round" />
        
        {/* 2. Pipe Body (Dark Slate Interior) */}
        <path d={d} fill="none" stroke="#1e293b" strokeWidth={width} strokeLinecap="round" strokeLinejoin="round" />
    </g>
);

// Layer 3, 4, 5: Fluid & Animation
export const PipeFluid: React.FC<{ d: string; isRunning: boolean; width?: number; flowColor?: string }> = ({ d, isRunning, width = 12, flowColor = "#38bdf8" }) => (
    <g>
        {/* 3. Liquid Base (Solid Color Fill) */}
        {/* Opacity is 1.0 to ensure solid looking fluid without joint artifacts */}
        <path 
            d={d} 
            fill="none" 
            stroke={flowColor} 
            strokeWidth={width - 2} 
            strokeOpacity={isRunning ? 1.0 : 0.05} 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            className="transition-all duration-1000"
        />

        {/* 4. Active Flow Animation (Dual Layer for volumetric effect) */}
        {isRunning && (
            <>
                 {/* Layer A: Fast, small bubbles/turbulence (High frequency) */}
                 <path 
                    d={d} 
                    fill="none" 
                    stroke="white" 
                    strokeWidth={width - 5} 
                    strokeDasharray="4 12" 
                    className="animate-flow-liquid" 
                    strokeOpacity="0.25" 
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    style={{ mixBlendMode: 'overlay', animationDuration: '2s' }}
                />
                
                {/* Layer B: Slow, large volume surges (Low frequency) */}
                 <path 
                    d={d} 
                    fill="none" 
                    stroke="white" 
                    strokeWidth={width - 2} 
                    strokeDasharray="40 120" 
                    className="animate-flow-liquid" 
                    strokeOpacity="0.1" 
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    style={{ mixBlendMode: 'screen', animationDuration: '4s' }} 
                />
            </>
        )}

        {/* 5. Static Pipe Gloss & Shading (Cylindrical Illusion) */}
        {/* Top Highlight (Sharp Gloss) */}
        <path 
            d={d} 
            fill="none" 
            stroke="white" 
            strokeWidth={2} 
            transform="translate(0, -2.5)" 
            strokeOpacity="0.15" 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            style={{ pointerEvents: 'none' }}
        />
        {/* Bottom Shadow (Roundness) */}
        <path 
            d={d} 
            fill="none" 
            stroke="black" 
            strokeWidth={3} 
            transform="translate(0, 3)" 
            strokeOpacity="0.1" 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            style={{ pointerEvents: 'none', mixBlendMode: 'multiply' }}
        />
    </g>
);

export const Flange: React.FC<{ x: number; y: number; orientation: 'vertical' | 'horizontal'; scale?: number }> = ({ x, y, orientation, scale = 1 }) => {
    return (
        <g transform={`translate(${x}, ${y}) scale(${scale})`}>
             <g transform={orientation === 'vertical' ? 'rotate(90)' : 'rotate(0)'}>
                {/* Left Plate */}
                <rect x="-4" y="-10" width="3" height="20" rx="0.5" fill="url(#metallic-gradient)" stroke="#0f172a" strokeWidth="1" />
                {/* Right Plate */}
                <rect x="1" y="-10" width="3" height="20" rx="0.5" fill="url(#metallic-gradient)" stroke="#0f172a" strokeWidth="1" />
                
                {/* Bolts */}
                <g fill="#94a3b8" stroke="#0f172a" strokeWidth="0.5">
                    <circle cx="-2.5" cy="-7" r="1.2" />
                    <circle cx="2.5" cy="-7" r="1.2" />
                    <circle cx="-2.5" cy="7" r="1.2" />
                    <circle cx="2.5" cy="7" r="1.2" />
                </g>
             </g>
        </g>
    );
};

// Default Orientation: T-Stem pointing Down.
// Ports: Left, Right, Bottom.
export const TeeFitting: React.FC<{ x: number; y: number; rotation?: number }> = ({ x, y, rotation = 0 }) => (
    <g transform={`translate(${x}, ${y}) rotate(${rotation})`}>
        {/* Main Body - Darkened to match pipes */}
        <path 
            d="M -12 -8 L 12 -8 L 12 8 L 8 8 L 8 14 L -8 14 L -8 8 L -12 8 Z" 
            fill="#1e293b" 
            stroke="#0f172a" 
            strokeWidth="1.5"
            strokeLinejoin="round"
        />
        
        {/* Flange Collars */}
        <rect x="-14" y="-10" width="2" height="16" fill="#475569" stroke="#0f172a" /> {/* Left */}
        <rect x="12" y="-10" width="2" height="16" fill="#475569" stroke="#0f172a" />  {/* Right */}
        <rect x="-8" y="14" width="16" height="2" fill="#475569" stroke="#0f172a" />   {/* Bottom */}
        
        {/* Center Weld/Detail */}
        <circle cx="0" cy="0" r="4" fill="none" stroke="#0f172a" strokeOpacity="0.2" />
    </g>
);

export const CheckValve: React.FC<{ x: number; y: number; rotation?: number }> = ({ x, y, rotation = 0 }) => (
    <g transform={`translate(${x}, ${y}) rotate(${rotation})`}>
        {/* Valve Body */}
        <circle cx="0" cy="0" r="10" fill="url(#metallic-gradient)" stroke="#0f172a" strokeWidth="1.5" />
        {/* Arrow/Symbol */}
        <path d="M -4 -4 L 4 0 L -4 4 Z" fill="#334155" stroke="#0f172a" strokeWidth="1" />
        <line x1="4" y1="-5" x2="4" y2="5" stroke="#0f172a" strokeWidth="1" />
        {/* Flanges */}
        <rect x="-12" y="-6" width="2" height="12" fill="#475569" stroke="#0f172a" />
        <rect x="10" y="-6" width="2" height="12" fill="#475569" stroke="#0f172a" />
    </g>
);

// --- ANIMATED DIVERTER VALVE ---
// Replaces static Tees with a 3-way motorized valve
export const ThreeWayValve: React.FC<{ 
    x: number; 
    y: number; 
    common: 'left' | 'right';
    direction: 'up' | 'down'; 
    flowColor?: string;
}> = ({ x, y, common, direction, flowColor = "#38bdf8" }) => {
    
    // Rotation Logic for "L" shaped internal ball valve
    // Base Shape L: Connects LEFT (-x) to TOP (-y)
    let rotation = 0;
    
    if (common === 'left') {
        // SUCTION SIDE (Common Inlet: Left)
        // If P-102 (Up) is Active: Need Left -> Up. (Matches Base Shape) -> Rot 0
        // If P-101 (Down) is Active: Need Left -> Down. 
        //    Rotate -90: Left(-x)->Bottom(+y), Top(-y)->Left(-x).  Result: Bottom-Left. Correct.
        if (direction === 'up') rotation = 0;
        else rotation = -90; 
    } else {
        // DISCHARGE SIDE (Common Outlet: Right)
        // If P-102 (Up) is Active: Need Up -> Right.
        //    Rotate 90: Left(-x)->Top(-y), Top(-y)->Right(+x). Result: Top-Right. Correct.
        // If P-101 (Down) is Active: Need Down -> Right.
        //    Rotate 180: Left(-x)->Right(+x), Top(-y)->Bottom(+y). Result: Right-Bottom. Correct.
        if (direction === 'up') rotation = 90;
        else rotation = 180;
    }

    return (
       <g transform={`translate(${x}, ${y})`}>
          <defs>
              <linearGradient id="valve-body-grad" x1="0" y1="0" x2="1" y2="1">
                  <stop offset="0%" stopColor="#334155" />
                  <stop offset="50%" stopColor="#475569" />
                  <stop offset="100%" stopColor="#1e293b" />
              </linearGradient>
              <filter id="valve-shadow">
                  <feDropShadow dx="1" dy="1" stdDeviation="1" floodOpacity="0.5"/>
              </filter>
          </defs>

          {/* 1. Connection Flanges (Static) */}
          {/* Vertical */}
          <rect x="-8" y="-18" width="16" height="4" fill="#475569" stroke="#0f172a" strokeWidth="0.5" />
          <rect x="-8" y="14" width="16" height="4" fill="#475569" stroke="#0f172a" strokeWidth="0.5" />
          {/* Horizontal */}
          <rect x={common === 'left' ? -18 : 14} y="-8" width="4" height="16" fill="#475569" stroke="#0f172a" strokeWidth="0.5" />

          {/* 2. Valve Body Housing */}
          <circle r="16" fill="url(#valve-body-grad)" stroke="#0f172a" strokeWidth="1.5" filter="url(#valve-shadow)" />
          
          {/* 3. Internal Rotating Plug (The Diverter) */}
          <g style={{ transform: `rotate(${rotation}deg)`, transition: 'transform 0.8s cubic-bezier(0.4, 0, 0.2, 1)' }}>
             {/* Ball Background */}
             <circle r="11" fill="#1e293b" stroke="#0f172a" strokeWidth="0.5" />
             
             {/* The Flow Channel (L-Shape) */}
             {/* Outline */}
             <path d="M -13 0 L 0 0 L 0 -13" fill="none" stroke="#000" strokeWidth="8" strokeLinecap="round" opacity="0.8" />
             {/* Fluid */}
             <path d="M -13 0 L 0 0 L 0 -13" fill="none" stroke={flowColor} strokeWidth="5" strokeLinecap="round" />
             
             {/* Center Pivot Point */}
             <circle r="2" fill="#475569" stroke="#0f172a" strokeWidth="0.5" />
          </g>

          {/* 4. Actuator (Motor) on Top */}
          <g transform="translate(0, 0)">
              {/* Bracket */}
              <rect x="-6" y="-6" width="12" height="12" rx="2" fill="none" stroke="#94a3b8" strokeWidth="1" opacity="0.5" />
              {/* Motor Box */}
              <rect x="-8" y="-8" width="8" height="8" rx="1" fill="#0f172a" stroke="#334155" strokeWidth="1" transform="translate(6, 6)" />
              {/* Indicator Light */}
              <circle cx="10" cy="10" r="1.5" fill={direction === 'up' ? "#10b981" : "#f59e0b"} className="animate-pulse" />
          </g>

       </g>
    );
};