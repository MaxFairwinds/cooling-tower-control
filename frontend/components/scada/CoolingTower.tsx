import React, { useMemo } from 'react';

// Helper to mix two colors (Hex or RGB) by 50%
const getMidColor = (c1: string, c2: string) => {
    const parse = (c: string) => {
        if (c.startsWith('#')) {
             if (c.length === 4) { // #RGB
                 return [
                    parseInt(c[1]+c[1], 16),
                    parseInt(c[2]+c[2], 16),
                    parseInt(c[3]+c[3], 16)
                 ];
             }
             const hex = c.slice(1);
             return [
                 parseInt(hex.substring(0, 2), 16),
                 parseInt(hex.substring(2, 4), 16),
                 parseInt(hex.substring(4, 6), 16)
             ];
        } else if (c.startsWith('rgb')) {
             const nums = c.match(/\d+/g);
             return nums ? [parseInt(nums[0]), parseInt(nums[1]), parseInt(nums[2])] : [0,0,0];
        }
        return [0,0,0]; // Fallback
    };
    
    const rgb1 = parse(c1);
    const rgb2 = parse(c2);
    
    const mix = [
        Math.round((rgb1[0] + rgb2[0]) / 2),
        Math.round((rgb1[1] + rgb2[1]) / 2),
        Math.round((rgb1[2] + rgb2[2]) / 2)
    ];
    
    return `rgb(${mix[0]},${mix[1]},${mix[2]})`;
};

// Ultra-Professional Mechanical Cooling Tower
export const CoolingTowerGraphic: React.FC<{ 
    x: number; 
    y: number; 
    waterLevel: boolean; 
    levelValue: number; 
    tempValue: number;
    isFanRunning: boolean;
    isWaterFlowing: boolean;
    waterColor?: string;
    returnColor?: string;
    steamIntensity?: number;
    frequency?: number; // New Prop for dynamic speed
}> = ({ 
    x, 
    y, 
    waterLevel, 
    levelValue, 
    tempValue, 
    isFanRunning, 
    isWaterFlowing, 
    waterColor = "#38bdf8", 
    returnColor = "#f97316", 
    steamIntensity = 0,
    frequency = 60 // Default to max speed if not provided
}) => {
    const id = `ct-${x}-${y}`;

    // Dimensions
    const width = 220;
    const legH = 50;
    const basinH = 110; 
    const bodyH = 160; 
    const stackH = 25; 
    
    // Calculated Y positions (Top to Bottom)
    const stackY = 0;
    const bodyY = stackY + stackH;
    const basinY = bodyY + bodyH;
    const legY = basinY + basinH;
    
    // Water Surface Y Calculation (relative to Basin group)
    const waterSurfaceY = 10 + (100 - levelValue) * 0.9;

    // Calculate the midpoint color for the hand-off between spray and fill
    const midColor = useMemo(() => getMidColor(returnColor, waterColor), [returnColor, waterColor]);

    // Calculate Animation Duration based on Frequency
    // 60Hz = Fast (~0.4s per rev)
    // 20Hz = Slow (~1.2s per rev)
    // Formula: 24 / freq
    const fanDuration = frequency > 0 ? (24 / Math.max(frequency, 1)) : 0;


    // MEMOIZED ANIMATION DATA (Prevents blinking on re-render)
    
    // 1. Basin Rain (Gravity Falls)
    const rainDrops = useMemo(() => [...Array(16)].map(() => ({
        cx: 40 + Math.random() * (width - 80),
        dur: 1.5 + Math.random() * 1.0, 
        begin: Math.random() * 2,
    })), [width]);

    // 2. Ripples
    const ripples = useMemo(() => [...Array(3)].map((_, i) => ({
        delay: i * 0.4,
        dur: 1.2 + i * 0.2
    })), []);

    // 3. Layer 1: Sheet Flow
    const flowSheets = useMemo(() => [...Array(8)].map((_, i) => ({
        x: 25 + i * 22,
        dur: 12 + Math.random() * 3,
        begin: Math.random()
    })), []);

    // 4. Layer 2: Drops falling down Fill (Friction/Surface Area)
    // Doubled density from 30 to 60 drops
    const mediaDrops = useMemo(() => [...Array(60)].map(() => ({
        cx: 25 + Math.random() * (width - 50),
        dur: 8 + Math.random() * 6, 
        begin: Math.random() * 10
    })), [width]);

    // 5. Layer 3: Spray Drops (Replacing Spray Nozzles Paths)
    const sprayDrops = useMemo(() => {
        const drops = [];
        const nozzleCount = 8;
        const dropsPerNozzle = 12; // High density for spray effect
        
        for (let i = 0; i < nozzleCount; i++) {
            // Nozzle tip X coordinate (28 start + index * spacing)
            const startX = 28 + i * 22;
            const startY = 20; // Corrected: Start at nozzle tip (Manifold 12 + Nozzle 8)
            
            for (let j = 0; j < dropsPerNozzle; j++) {
                // Cone spread: Drops spread out in X as they fall
                const spread = (Math.random() - 0.5) * 20; // +/- 10px spread
                
                drops.push({
                    startX: startX,
                    startY: startY,
                    endX: startX + spread,
                    endY: startY + 30 + Math.random() * 25, // Fall distance 30-55px
                    // Slowed down spray pattern by half (1.2s base instead of 0.6s)
                    dur: 1.2 + Math.random() * 1.2, 
                    delay: Math.random() * 1.0, // Staggered start
                    r: 0.5 + Math.random() * 0.6 // Varying drop sizes
                });
            }
        }
        return drops;
    }, []);

    // 6. STEAM PARTICLES (Generated based on max potential load)
    const steamParticles = useMemo(() => [...Array(15)].map((_, i) => ({
        cx: width / 2 + (Math.random() - 0.5) * 30, // Start roughly centered in stack
        rx: 15 + Math.random() * 15,
        ry: 8 + Math.random() * 8,
        drift: (Math.random() - 0.5) * 80, // Drift left or right as it rises
        riseHeight: 120 + Math.random() * 80, // How high it goes
        dur: 2 + Math.random() * 2,
        delay: Math.random() * 3,
        scaleEnd: 2 + Math.random(), // Puff expands
    })), [width]);

    // 7. SMALL STEAM PARTICLES
    const smallSteamParticles = useMemo(() => [...Array(10)].map((_, i) => ({
        cx: width / 2 + (Math.random() - 0.5) * 20,
        rx: 8 + Math.random() * 8,
        ry: 4 + Math.random() * 4,
        drift: (Math.random() - 0.5) * 60,
        riseHeight: 80 + Math.random() * 60,
        dur: 1.5 + Math.random() * 1.5,
        delay: Math.random() * 2,
        scaleEnd: 1.5 + Math.random(),
    })), [width]);

    // 8. FAN BLADE ANIMATION HELPERS
    // Single blade shape defined from Root (0,0) to Tip (90,0)
    // Twisted Airfoil shape: Wide chord near root, tapering to tip.
    const bladePath = "M 0 3 Q 30 14 90 4 L 92 0 L 90 -4 Q 30 -14 0 -3 Z";
    
    // We create 4 blades, offset by 0.25s (90 degrees)
    // Config for Static "Parked" State:
    // 0: Right (Front layer, Scale 1)
    // 1: Back (Rear layer, Scale 0.25)
    // 2: Left (Rear layer, Scale -1)
    // 3: Front (Front layer, Scale -0.25)
    const bladeConfigs = [
        { offset: 0,    staticScale: 1,     staticLayer: 'rear' },  // Right Blade (Sticking out right, behind hub)
        { offset: 0.25, staticScale: 0.25,  staticLayer: 'rear' },  // Back Blade (Hidden behind hub mostly)
        { offset: 0.5,  staticScale: -1,    staticLayer: 'rear' },  // Left Blade (Sticking out left, behind hub)
        { offset: 0.75, staticScale: -0.25, staticLayer: 'front' }  // Front Blade (Visible on top of hub)
    ];

    const BladeElement: React.FC<{ config: typeof bladeConfigs[0]; layer: 'front' | 'rear' }> = ({ config, layer }) => {
        const { offset, staticScale, staticLayer } = config;
        
        // If stopped, only render if the layer matches the static configuration
        if (!isFanRunning && layer !== staticLayer) return null;

        // Animation Logic:
        // Cycle: Right (1) -> Back (0.15) -> Left (-1) -> Front (-0.15) -> Right (1)
        // Time:  0%          25%            50%           75%             100%
        
        // REAR Layer Visibility: Visible when blade is in BACK semi-circle (0% -> 50%)
        // FRONT Layer Visibility: Visible when blade is in FRONT semi-circle (50% -> 100%)
        
        const opacityValues = layer === 'rear' 
            ? "1; 1; 0; 0; 1"  // Visible 0-0.5
            : "0; 0; 1; 1; 0"; // Visible 0.5-1
            
        // KeyTimes matched to the switch points (slightly padded to avoid flickering)
        const opacityKeyTimes = "0; 0.499; 0.5; 0.999; 1";

        return (
            <g>
                <path 
                    d={bladePath} 
                    fill={`url(#${id}-blade-h)`} 
                    stroke="#0f172a" 
                    strokeWidth="0.5"
                    transform={!isFanRunning ? `scale(${staticScale} 1)` : undefined} // Static Transform
                >
                    {isFanRunning && (
                        <>
                            {/* Rotation Simulation (Scale X) */}
                            {/* Uses 0.15 min scale to show blade "twist" width when edge-on */}
                            <animateTransform 
                                attributeName="transform" 
                                type="scale" 
                                values="1 1; 0.15 1; -1 1; -0.15 1; 1 1" 
                                keyTimes="0; 0.25; 0.5; 0.75; 1"
                                calcMode="spline"
                                keySplines="0.45 0 0.55 1; 0.45 0 0.55 1; 0.45 0 0.55 1; 0.45 0 0.55 1"
                                dur={`${fanDuration}s`}
                                begin={`${-offset * fanDuration}s`}
                                repeatCount="indefinite" 
                            />
                            {/* Layer Swapping (Z-Index Simulation) */}
                            <animate 
                                attributeName="opacity" 
                                values={opacityValues} 
                                keyTimes={opacityKeyTimes}
                                dur={`${fanDuration}s`} 
                                begin={`${-offset * fanDuration}s`}
                                repeatCount="indefinite" 
                            />
                        </>
                    )}
                </path>
                {/* Highlight Line for gloss */}
                <path 
                    d="M 5 0 L 85 0" 
                    stroke="white" 
                    strokeOpacity="0.3" 
                    strokeWidth="1" 
                    fill="none"
                    transform={!isFanRunning ? `scale(${staticScale} 1)` : undefined}
                >
                    {isFanRunning && (
                        <>
                           <animateTransform 
                                attributeName="transform" type="scale" 
                                values="1 1; 0.15 1; -1 1; -0.15 1; 1 1" 
                                keyTimes="0; 0.25; 0.5; 0.75; 1"
                                calcMode="spline"
                                keySplines="0.45 0 0.55 1; 0.45 0 0.55 1; 0.45 0 0.55 1; 0.45 0 0.55 1"
                                dur={`${fanDuration}s`}
                                begin={`${-offset * fanDuration}s`}
                                repeatCount="indefinite" 
                           />
                           <animate 
                                attributeName="opacity" 
                                values={opacityValues} 
                                keyTimes={opacityKeyTimes}
                                dur={`${fanDuration}s`} 
                                begin={`${-offset * fanDuration}s`}
                                repeatCount="indefinite" 
                            />
                        </>
                    )}
                </path>
            </g>
        );
    };

    return (
    <g transform={`translate(${x - 110}, ${y - 30}) scale(1.1)`}>
        <defs>
             {/* Texture: Fill Media - Enhanced Cross Hatch Definition */}
             <pattern id={`${id}-fill-uniform`} width="12" height="12" patternUnits="userSpaceOnUse">
                {/* Darker Background for Fill Area */}
                <rect width="12" height="12" fill="#020617" />
                {/* Thinner lines for lighter weight */}
                <line x1="0" y1="11" x2="12" y2="11" stroke="#64748b" strokeWidth="0.5" opacity="0.4" />
                {/* Criss-Cross for better definition - Thinner */}
                <path d="M 0 0 L 12 12" stroke="#475569" strokeWidth="0.5" opacity="0.6" />
                <path d="M 12 0 L 0 12" stroke="#475569" strokeWidth="0.5" opacity="0.6" />
            </pattern>

            <linearGradient id="industrial-metal" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#0f172a" /> 
                <stop offset="10%" stopColor="#334155" /> 
                <stop offset="50%" stopColor="#475569" /> 
                <stop offset="90%" stopColor="#334155" />
                <stop offset="100%" stopColor="#0f172a" />
            </linearGradient>

             {/* Revised Silver Glass Gradient for Shroud */}
             <linearGradient id="silver-glass" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#94a3b8" stopOpacity="0.4" />
                <stop offset="20%" stopColor="#f8fafc" stopOpacity="0.6" />
                <stop offset="50%" stopColor="#e2e8f0" stopOpacity="0.2" /> {/* Transparent Center */}
                <stop offset="80%" stopColor="#f8fafc" stopOpacity="0.6" />
                <stop offset="100%" stopColor="#94a3b8" stopOpacity="0.4" />
            </linearGradient>

            <linearGradient id="fan-blade-composite" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#334155" /> 
                <stop offset="50%" stopColor="#64748b" /> 
                <stop offset="100%" stopColor="#1e293b" /> 
            </linearGradient>
            
             <linearGradient id="concrete" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#334155" /> 
                <stop offset="100%" stopColor="#1e293b" /> 
            </linearGradient>

            {/* Flow Gradient: Transitions from Hot Return (Top) to Cold Supply (Bottom) */}
            <linearGradient id={`${id}-flow-grad`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={returnColor} stopOpacity="0.7" />
                <stop offset="10%" stopColor={returnColor} stopOpacity="0.6" />
                <stop offset="20%" stopColor={waterColor} stopOpacity="0.5" />
                <stop offset="100%" stopColor={waterColor} stopOpacity="0.3" />
            </linearGradient>

            {/* NEW: Horizontal blade gradient for better definition - DARKENED */}
            <linearGradient id={`${id}-blade-h`} x1="0" y1="0" x2="1" y2="0">
                 <stop offset="0%" stopColor="#64748b" /> {/* Darker Slate */}
                 <stop offset="50%" stopColor="#94a3b8" /> {/* Medium Slate */}
                 <stop offset="100%" stopColor="#64748b" /> {/* Darker Slate */}
            </linearGradient>
            
             {/* NEW: Vertical Casing Gradient (Metallic Sheen) */}
             <linearGradient id={`${id}-casing-v`} x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#1e293b" />   {/* Dark Edge */}
                <stop offset="15%" stopColor="#475569" />  {/* Highlight */}
                <stop offset="50%" stopColor="#334155" />  {/* Mid */}
                <stop offset="85%" stopColor="#475569" />  {/* Highlight */}
                <stop offset="100%" stopColor="#1e293b" /> {/* Dark Edge */}
            </linearGradient>

             {/* NEW: Structural Steel Gradient */}
            <linearGradient id={`${id}-steel-leg`} x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#0f172a" />
                <stop offset="20%" stopColor="#334155" />
                <stop offset="50%" stopColor="#1e293b" />
                <stop offset="100%" stopColor="#020617" />
            </linearGradient>

            {/* NEW: Concrete Basin Texture */}
            <pattern id={`${id}-concrete-pat`} width="8" height="8" patternUnits="userSpaceOnUse">
                 <rect width="8" height="8" fill="#334155" />
                 <circle cx="2" cy="2" r="0.5" fill="#475569" />
                 <circle cx="6" cy="6" r="0.5" fill="#1e293b" />
            </pattern>
            
            {/* Water Depth Gradient for Basin - Surface matches pipe color, deepens at bottom */}
            <linearGradient id={`${id}-water-depth`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={waterColor} stopOpacity="1" />
                <stop offset="100%" stopColor="#0f172a" stopOpacity="0.8" />
            </linearGradient>

             {/* STEAM FILTER */}
             {/* Uses heavy blur and displacement to create cloud puffs from simple ellipses */}
             <filter id={`${id}-steam-blur`} x="-100%" y="-200%" width="300%" height="300%">
                 <feGaussianBlur in="SourceGraphic" stdDeviation="8" result="blur" />
                 <feColorMatrix in="blur" mode="matrix" values="1 0 0 0 1  0 1 0 0 1  0 0 1 0 1  0 0 0 18 -9" result="goo" />
                 <feComposite in="SourceGraphic" in2="goo" operator="atop"/>
                 <feGaussianBlur stdDeviation="5" />
             </filter>
        </defs>
        
        {/* LEGS: Improved 3D Structural Steel Look */}
        <g transform={`translate(0, ${legY})`}>
            {/* Left Leg (I-Beam) */}
            <rect x="20" y="0" width="12" height={legH} fill={`url(#${id}-steel-leg)`} stroke="#0f172a" />
            <path d="M 20 0 L 22 0 L 22 50 L 20 50 Z" fill="#475569" opacity="0.5" /> {/* Highlight edge */}
            
            {/* Right Leg (I-Beam) */}
            <rect x={width - 32} y="0" width="12" height={legH} fill={`url(#${id}-steel-leg)`} stroke="#0f172a" />
            <path d={`M ${width - 32} 0 L ${width - 30} 0 L ${width - 30} 50 L ${width - 32} 50 Z`} fill="#475569" opacity="0.5" />

            {/* Center Support */}
             <rect x={width/2 - 6} y="0" width="12" height={legH} fill={`url(#${id}-steel-leg)`} stroke="#0f172a" />

            {/* Cross Bracing - Structural X pattern with depth */}
            {/* Left Cross */}
            <path d={`M 32 5 L ${width/2 - 6} ${legH-5}`} stroke="#0f172a" strokeWidth="4" />
            <path d={`M 32 5 L ${width/2 - 6} ${legH-5}`} stroke="#334155" strokeWidth="2" /> {/* Inner highlight */}
            <path d={`M ${width/2 - 6} 5 L 32 ${legH-5}`} stroke="#0f172a" strokeWidth="4" />
            <path d={`M ${width/2 - 6} 5 L 32 ${legH-5}`} stroke="#334155" strokeWidth="2" />

            {/* Right Cross */}
            <path d={`M ${width/2 + 6} 5 L ${width - 32} ${legH-5}`} stroke="#0f172a" strokeWidth="4" />
            <path d={`M ${width/2 + 6} 5 L ${width - 32} ${legH-5}`} stroke="#334155" strokeWidth="2" />
            <path d={`M ${width - 32} 5 L ${width/2 + 6} ${legH-5}`} stroke="#0f172a" strokeWidth="4" />
            <path d={`M ${width - 32} 5 L ${width/2 + 6} ${legH-5}`} stroke="#334155" strokeWidth="2" />
        </g>

        {/* BASIN: Concrete Pan with Rim */}
        <g transform={`translate(0, ${basinY})`}>
            {/* Main Basin Shape */}
             <path d={`M 10 0 L ${width-10} 0 L ${width-15} ${basinH} L 15 ${basinH} Z`} fill={`url(#${id}-concrete-pat)`} stroke="#0f172a" strokeWidth="2" />
             {/* Shading gradient overlay for curvature/depth */}
             <path d={`M 10 0 L ${width-10} 0 L ${width-15} ${basinH} L 15 ${basinH} Z`} fill="url(#industrial-metal)" opacity="0.3" style={{ mixBlendMode: 'multiply' }} pointerEvents="none" />

            {/* Top Rim/Flange of Basin */}
            <rect x="0" y="-4" width={width} height="8" rx="2" fill={`url(#${id}-casing-v)`} stroke="#0f172a" />
            <line x1="0" y1="0" x2={width} y2="0" stroke="#000" strokeOpacity="0.3" />
            
            {waterLevel && (
                <g>
                   <path d={`M 30 10 L ${width-30} 10 L ${width-35} ${basinH-10} L 35 ${basinH-10} Z`} fill="#0f172a" opacity="0.5" />
                   
                   {/* Main Water Body - Using Depth Gradient */}
                   <rect x="30" y={waterSurfaceY} width={width-60} height={basinH - 10 - waterSurfaceY} fill={`url(#${id}-water-depth)`} />
                   
                   {/* Animated Surface Tension Line - Gentle Wave */}
                   {isWaterFlowing && (
                       <path 
                         d={`M 30 ${waterSurfaceY} Q ${width/2} ${waterSurfaceY + 2} ${width-30} ${waterSurfaceY}`} 
                         stroke="white" 
                         strokeWidth="1.5" 
                         fill="none" 
                         opacity="0.4"
                       >
                           <animate 
                             attributeName="d" 
                             values={`M 30 ${waterSurfaceY} Q ${width/2} ${waterSurfaceY + 2} ${width-30} ${waterSurfaceY};
                                      M 30 ${waterSurfaceY} Q ${width/2} ${waterSurfaceY - 1} ${width-30} ${waterSurfaceY};
                                      M 30 ${waterSurfaceY} Q ${width/2} ${waterSurfaceY + 2} ${width-30} ${waterSurfaceY}`} 
                             dur="3s" 
                             repeatCount="indefinite" 
                           />
                       </path>
                   )}
                   {!isWaterFlowing && (
                       <line x1="30" y1={waterSurfaceY} x2={width-30} y2={waterSurfaceY} stroke="white" strokeWidth="1" opacity="0.3" />
                   )}
                   
                   {/* Improved Ripples (Multi-Ring) */}
                   {isWaterFlowing && ripples.map((r, i) => (
                       <g key={`splash-${i}`} transform={`translate(${40 + i * 50}, ${waterSurfaceY})`}>
                            {/* Inner Ring */}
                            <ellipse cx="0" cy="0" rx="0" ry="0" fill="none" stroke="white" strokeWidth="1">
                                <animate attributeName="rx" values="0;12" dur={`${r.dur}s`} repeatCount="indefinite" begin={`${r.delay}s`} />
                                <animate attributeName="ry" values="0;3" dur={`${r.dur}s`} repeatCount="indefinite" begin={`${r.delay}s`} />
                                <animate attributeName="opacity" values="0.8;0" dur={`${r.dur}s`} repeatCount="indefinite" begin={`${r.delay}s`} />
                            </ellipse>
                            {/* Outer Ring */}
                             <ellipse cx="0" cy="0" rx="0" ry="0" fill="none" stroke="white" strokeWidth="0.5">
                                <animate attributeName="rx" values="0;20" dur={`${r.dur}s`} repeatCount="indefinite" begin={`${r.delay + 0.1}s`} />
                                <animate attributeName="ry" values="0;5" dur={`${r.dur}s`} repeatCount="indefinite" begin={`${r.delay + 0.1}s`} />
                                <animate attributeName="opacity" values="0.6;0" dur={`${r.dur}s`} repeatCount="indefinite" begin={`${r.delay + 0.1}s`} />
                            </ellipse>
                       </g>
                   ))}
                </g>
            )}

            {/* Basin Rain - Gravity Drop */}
            {isWaterFlowing && waterLevel && (
                <g>
                    {rainDrops.map((d, i) => (
                        <ellipse 
                            key={`drop-${i}`}
                            cx={d.cx}
                            cy={-5}
                            rx="0.8" 
                            ry="1.5"
                            fill={waterColor}
                            opacity="0.8"
                        >
                            <animate 
                                attributeName="cy" 
                                from="-5" 
                                to={waterSurfaceY} 
                                dur={`${d.dur}s`} 
                                repeatCount="indefinite" 
                                begin={`${d.begin}s`}
                                calcMode="spline"
                                keyTimes="0;1"
                                keySplines="0.4 0 1 1" // Ease-In (simulating gravity acceleration)
                            />
                            {/* Stretch as they accelerate */}
                            <animate 
                                attributeName="ry" 
                                values="1.5;12" 
                                dur={`${d.dur}s`} 
                                repeatCount="indefinite" 
                                begin={`${d.begin}s`}
                                calcMode="spline"
                                keyTimes="0;1"
                                keySplines="0.4 0 1 1"
                            />
                            <animate 
                                attributeName="opacity" 
                                values="0;0.9;0" 
                                keyTimes="0;0.1;1"
                                dur={`${d.dur}s`} 
                                repeatCount="indefinite" 
                                begin={`${d.begin}s`}
                            />
                        </ellipse>
                    ))}
                </g>
            )}

            {/* Level Reading Overlay */}
            {waterLevel && (
                 <g transform={`translate(${width/2}, ${basinH/2 + 20})`}>
                    <rect x="-24" y="-8" width="48" height="16" rx="3" fill="#0f172a" fillOpacity="0.8" stroke="#334155" strokeWidth="1" />
                    <text x="0" y="3" textAnchor="middle" className="text-[10px] font-mono font-bold fill-sky-400 tracking-wider">
                        {levelValue.toFixed(0)}%
                    </text>
                </g>
            )}
        </g>
        
        {/* GEARBOX / MOTOR - Rendered BEFORE Body so it appears behind the nozzle header */}
        <g transform={`translate(${width/2}, ${stackY + 10})`}>
             {/* 1. GEARBOX / MOTOR HOUSING (Detailed) */}
             {/* Main Housing Block */}
             <rect x="-10" y="5" width="20" height="25" fill="#334155" stroke="#0f172a" strokeWidth="1" />
             {/* Cooling Fins (Horizontal Lines) */}
             {[8, 14, 20, 26].map(fy => (
                 <line key={`fin-${fy}`} x1="-10" y1={fy} x2="10" y2={fy} stroke="#0f172a" strokeWidth="0.5" strokeOpacity="0.5" />
             ))}
             {/* Vertical Reinforcement Rib */}
             <line x1="0" y1="5" x2="0" y2="30" stroke="#0f172a" strokeWidth="0.5" strokeOpacity="0.5" />
        </g>

        {/* BODY: Industrial Panels and Frame */}
        <g transform={`translate(0, ${bodyY})`}>
             {/* Main Frame Columns (Steel) */}
             <rect x="10" y="0" width="10" height={bodyH} fill={`url(#${id}-steel-leg)`} stroke="#0f172a" />
             <rect x={width-20} y="0" width="10" height={bodyH} fill={`url(#${id}-steel-leg)`} stroke="#0f172a" />
             
             {/* Center Column */}
             <rect x={width/2 - 5} y="0" width="10" height={bodyH} fill={`url(#${id}-steel-leg)`} stroke="#0f172a" />

             {/* Horizontal Beams */}
             <rect x="10" y="0" width={width-20} height="8" fill={`url(#${id}-steel-leg)`} stroke="#0f172a" />
             <rect x="10" y={bodyH/2 - 4} width={width-20} height="8" fill={`url(#${id}-steel-leg)`} stroke="#0f172a" />
             <rect x="10" y={bodyH - 8} width={width-20} height="8" fill={`url(#${id}-steel-leg)`} stroke="#0f172a" />

             {/* Fill Media Background (Recessed Panels) */}
             {/* Left Panel Top */}
             <rect x="20" y="8" width={width/2 - 25} height={bodyH/2 - 12} fill={`url(#${id}-fill-uniform)`} stroke="#000" strokeOpacity="0.5" />
             {/* Left Panel Bottom */}
             <rect x="20" y={bodyH/2 + 4} width={width/2 - 25} height={bodyH/2 - 12} fill={`url(#${id}-fill-uniform)`} stroke="#000" strokeOpacity="0.5" />
             
             {/* Right Panel Top */}
             <rect x={width/2 + 5} y="8" width={width/2 - 25} height={bodyH/2 - 12} fill={`url(#${id}-fill-uniform)`} stroke="#000" strokeOpacity="0.5" />
             {/* Right Panel Bottom */}
             <rect x={width/2 + 5} y={bodyH/2 + 4} width={width/2 - 25} height={bodyH/2 - 12} fill={`url(#${id}-fill-uniform)`} stroke="#000" strokeOpacity="0.5" />
            
            {/* Water Flow ("Curtain") */}
            {isWaterFlowing && (
                <>
                    {/* Layer 1: The Sheet/Column Flow */}
                    <g opacity="0.3">
                        {flowSheets.map((s, i) => (
                             <rect 
                                key={`flow-${i}`}
                                x={s.x}
                                y="20" // Corrected: Start below new nozzles
                                width="6"
                                height={bodyH - 20}
                                fill={`url(#${id}-flow-grad)`}
                             >
                                 <animate 
                                    attributeName="opacity" 
                                    values="0.3;0.7;0.3" 
                                    dur={`${s.dur}s`} 
                                    repeatCount="indefinite" 
                                    begin={`${s.begin}s`}
                                 />
                             </rect>
                        ))}
                    </g>
                    
                    {/* Layer 2: Slow Dripping Drops Overlay - MEDIA FRICTION */}
                    <g>
                        {mediaDrops.map((d, i) => (
                            <circle
                                key={`media-drop-${i}`}
                                cx={d.cx}
                                cy={35} // Start position moved down to ~50% of spray height (Nozzle 14 + ~21)
                                r={1.2}
                                fill={midColor} // Start with the midpoint color
                            >
                                <animate
                                    attributeName="cy"
                                    from="35" // Animation starts where the spray hands off
                                    to={bodyH}
                                    dur={`${d.dur}s`}
                                    repeatCount="indefinite"
                                    begin={`${d.begin}s`}
                                />
                                {/* Slow Blinking Opacity: 100% to 20% oscillation */}
                                <animate
                                    attributeName="opacity"
                                    values="0;0.2;1;0.2;1;0.2;0"
                                    keyTimes="0;0.05;0.25;0.5;0.75;0.95;1"
                                    dur={`${d.dur}s`}
                                    repeatCount="indefinite"
                                    begin={`${d.begin}s`}
                                />
                                {/* Color Transition: Midpoint (Mix) -> Cold (Supply) */}
                                <animate 
                                    attributeName="fill"
                                    values={`${midColor};${waterColor}`}
                                    dur={`${d.dur}s`}
                                    repeatCount="indefinite"
                                    begin={`${d.begin}s`}
                                />
                            </circle>
                        ))}
                    </g>
                    
                    {/* Layer 3: Spray Drops - NOZZLE CONES */}
                    <g>
                        {sprayDrops.map((d, i) => (
                            <circle
                                key={`spray-drop-${i}`}
                                cx={d.startX}
                                cy={d.startY}
                                r={d.r}
                                fill={returnColor} // Initial fill
                                opacity="0.5" // CHANGED TO 50%
                            >
                                <animate
                                    attributeName="cx"
                                    from={d.startX}
                                    to={d.endX}
                                    dur={`${d.dur}s`}
                                    repeatCount="indefinite"
                                    begin={`${d.delay}s`}
                                />
                                <animate
                                    attributeName="cy"
                                    from={d.startY}
                                    to={d.endY}
                                    dur={`${d.dur}s`}
                                    repeatCount="indefinite"
                                    begin={`${d.delay}s`}
                                />
                                <animate
                                    attributeName="opacity"
                                    values="0;0.8;0"
                                    keyTimes="0;0.2;1"
                                    dur={`${d.dur}s`}
                                    repeatCount="indefinite"
                                    begin={`${d.delay}s`}
                                />
                                {/* Color Transition: Hot (Return) -> Cold (Supply) */}
                                <animate 
                                    attributeName="fill"
                                    values={`${returnColor};${waterColor}`}
                                    dur={`${d.dur}s`}
                                    repeatCount="indefinite"
                                    begin={`${d.delay}s`}
                                />
                            </circle>
                        ))}
                    </g>
                </>
            )}
            
            {/* Distribution System: Manifold & Nozzles */}
            <g>
                {/* Main Manifold Header - Connecting to Inlet */}
                <rect x="15" y="0" width={width - 30} height="12" rx="2" fill="url(#industrial-metal)" stroke="#0f172a" strokeWidth="1" />
                
                {/* Visual connection to inlet flange at top right */}
                {/* The inlet flange (rendered later/above) comes down to y=0 at x=width-25. 
                    It sits perfectly on top of this rect. */}

                {/* Nozzles mounted on bottom */}
                {[...Array(8)].map((_, i) => {
                     const nx = 28 + i * 22;
                     return (
                         <g key={`nozzle-${i}`}>
                             {/* Nozzle Fitting/Neck */}
                             <rect x={nx - 3} y="12" width="6" height="3" fill="#334155" stroke="#0f172a" strokeWidth="0.5" />
                             {/* Nozzle Cone */}
                             <path 
                                d={`M ${nx - 4} 15 L ${nx + 4} 15 L ${nx} 20 Z`} 
                                fill="#475569" 
                                stroke="#0f172a" 
                                strokeWidth="0.5" 
                             />
                         </g>
                     );
                })}
            </g>

            {/* Inlet Header (New Flange) at Top Center of Body */}
            <g transform={`translate(${width - 25}, 0)`}>
                {/* Neck */}
                <rect x="-8" y="-10" width="16" height="10" fill="#334155" stroke="#0f172a" />
                {/* Flange Plate */}
                <rect x="-14" y="-14" width="28" height="4" fill="#475569" stroke="#0f172a" rx="1" />
                {/* Bolts */}
                <circle cx="-10" cy="-12" r="1.5" fill="#1e293b" />
                <circle cx="10" cy="-12" r="1.5" fill="#1e293b" />
            </g>
        </g>
        
        {/* FAN DECK & STACK - Completely Orthographic Side View */}
        <g transform={`translate(0, ${stackY})`}>
             {/* Fan Deck (Base Platform) - Molded Fiberglass Look */}
             <rect x="0" y={stackH} width={width} height="12" fill={`url(#${id}-casing-v)`} stroke="#0f172a" />
             
             {/* FAN STACK (Cylinder Side View) - Shorter Stack (25px) */}
             {/* Main Cylinder with DARK SHROUD INTERIOR */}
             <path d={`M 15 0 L ${width-15} 0 L ${width-15} ${stackH} L 15 ${stackH} Z`} fill="url(#shroud-interior)" stroke="#0f172a" strokeWidth="1" />
             
             {/* Texture/Ribs on stack */}
             <line x1="15" y1="12" x2={width-15} y2="12" stroke="#000" strokeOpacity="0.2" />

             {/* Top Lip of Stack (Reinforced Edge) */}
             <path d={`M 12 -2 L ${width-12} -2 L ${width-15} 0 L 15 0 Z`} fill="#334155" stroke="#0f172a" />

             {/* FAN ASSEMBLY (Inside Stack) - Lowered by 10px from top (y=10) */}
             <g transform={`translate(${width/2}, 10)`}>
                 {/* Gearbox moved to separate group before body */}
                 
                 {/* Motion Blur Disk (Only visible when running) - Background layer */}
                 {isFanRunning && (
                    <ellipse cx="0" cy="0" rx="92" ry="6" fill="#000" opacity="0.1" filter="blur(2px)" />
                 )}
                 
                 {/* GROUP 1: REAR BLADES (Rendered BEHIND Hub) */}
                 {bladeConfigs.map((config, i) => (
                    <BladeElement key={`blade-rear-${i}`} config={config} layer="rear" />
                 ))}
                 
                 {/* 2. ROTATING HUB ASSEMBLY */}
                 {/* Hub Plate (Base) - Wider and more mechanical */}
                 <rect x="-16" y="-6" width="32" height="10" rx="2" fill="#475569" stroke="#0f172a" strokeWidth="1" />
                 
                 {/* Blade Clamp Details (Visual blocks where blades attach) */}
                 <rect x="-18" y="-4" width="4" height="6" rx="1" fill="#334155" stroke="#0f172a" strokeWidth="0.5" />
                 <rect x="14" y="-4" width="4" height="6" rx="1" fill="#334155" stroke="#0f172a" strokeWidth="0.5" />

                 {/* Hub Bolts */}
                 <circle cx="-10" cy="-1" r="1.2" fill="#1e293b" />
                 <circle cx="10" cy="-1" r="1.2" fill="#1e293b" />
                 <circle cx="0" cy="1" r="1.2" fill="#1e293b" />
                 
                 {/* 3. AERODYNAMIC SPINNER CAP (Top) - Curved Nose Cone */}
                 <path 
                    d="M -14 -6 C -14 -16, -6 -20, 0 -22 C 6 -20, 14 -16, 14 -6 Z" 
                    fill="url(#fan-blade-composite)" 
                    stroke="#0f172a" 
                    strokeWidth="1" 
                 />
                 {/* Spinner Highlight/Gloss for 3D effect */}
                 <path 
                    d="M -8 -8 Q -4 -16 0 -18" 
                    fill="none" 
                    stroke="white" 
                    strokeWidth="1" 
                    strokeOpacity="0.3" 
                 />
                 
                 {/* Center Locking Bolt on Cap */}
                 <ellipse cx="0" cy="-6" rx="6" ry="2" fill="#334155" stroke="#0f172a" strokeWidth="0.5" />
                 <circle cx="0" cy="-6" r="1" fill="#0f172a" />
                 
                 {/* GROUP 2: FRONT BLADES (Rendered IN FRONT OF Hub) */}
                 {bladeConfigs.map((config, i) => (
                    <BladeElement key={`blade-front-${i}`} config={config} layer="front" />
                 ))}
             </g>

             {/* Fan Guard (Top Screen) */}
             <line x1="10" y1="0" x2={width-10} y2="0" stroke="#475569" strokeWidth="2" />
        </g>
        
        {/* STEAM PLUME - RENDERED BEHIND LABEL BUT ABOVE STACK */}
        {/* Only visible if fan is running and intensity > 0.05 */}
        {isFanRunning && steamIntensity > 0.05 && (
            <g transform={`translate(0, ${stackY - 20})`} filter={`url(#${id}-steam-blur)`}>
                {/* Layer 1: Standard Particles (Reduced Opacity) */}
                {steamParticles.map((p, i) => (
                    <ellipse
                        key={`steam-${i}`}
                        cx={p.cx}
                        cy="20" // Start inside the stack
                        rx={p.rx}
                        ry={p.ry}
                        fill="#fff"
                    >
                         {/* Upward Movement */}
                         <animate 
                            attributeName="cy"
                            from="20"
                            to={-p.riseHeight}
                            dur={`${p.dur}s`}
                            repeatCount="indefinite"
                            begin={`${p.delay}s`}
                        />
                        {/* Horizontal Drift (Wind/Turbulence) */}
                        <animate 
                            attributeName="cx"
                            from={p.cx}
                            to={p.cx + p.drift}
                            dur={`${p.dur}s`}
                            repeatCount="indefinite"
                            begin={`${p.delay}s`}
                        />
                        {/* Expansion (Dissipation) */}
                        <animateTransform 
                            attributeName="transform"
                            type="scale"
                            from="1 1"
                            to={`${p.scaleEnd} ${p.scaleEnd}`}
                            dur={`${p.dur}s`}
                            repeatCount="indefinite"
                            begin={`${p.delay}s`}
                        />
                        {/* Opacity reduced from 0.4 to 0.2 */}
                        <animate 
                            attributeName="opacity"
                            values={`0;${steamIntensity * 0.2};0`} 
                            dur={`${p.dur}s`}
                            repeatCount="indefinite"
                            begin={`${p.delay}s`}
                        />
                    </ellipse>
                ))}

                {/* Layer 2: Small Particles (50% size) */}
                {smallSteamParticles.map((p, i) => (
                    <ellipse
                        key={`steam-small-${i}`}
                        cx={p.cx}
                        cy="20"
                        rx={p.rx}
                        ry={p.ry}
                        fill="#fff"
                    >
                         <animate attributeName="cy" from="20" to={-p.riseHeight} dur={`${p.dur}s`} repeatCount="indefinite" begin={`${p.delay}s`} />
                         <animate attributeName="cx" from={p.cx} to={p.cx + p.drift} dur={`${p.dur}s`} repeatCount="indefinite" begin={`${p.delay}s`} />
                         <animateTransform attributeName="transform" type="scale" from="1 1" to={`${p.scaleEnd} ${p.scaleEnd}`} dur={`${p.dur}s`} repeatCount="indefinite" begin={`${p.delay}s`} />
                         <animate attributeName="opacity" values={`0;${steamIntensity * 0.2};0`} dur={`${p.dur}s`} repeatCount="indefinite" begin={`${p.delay}s`} />
                    </ellipse>
                ))}
            </g>
        )}

        {/* LABEL */}
        <g transform={`translate(${width/2}, ${legY + 25})`}>
            <rect x="-40" y="-8" width="80" height="16" rx="2" fill="#0f172a" stroke="#334155" />
            <text x="0" y="3" textAnchor="middle" className="text-[9px] font-mono font-bold fill-white tracking-widest">CT-01</text>
            <circle cx="-32" cy="0" r="2" fill={isFanRunning ? "#10b981" : "#64748b"} />
            <circle cx="32" cy="0" r="2" fill={isFanRunning ? "#10b981" : "#64748b"} />
        </g>

    </g>
    );
}