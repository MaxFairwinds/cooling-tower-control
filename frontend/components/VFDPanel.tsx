import React, { useState, useEffect } from 'react';
import { Play, Square, AlertCircle, Cpu, Gauge, Settings2 } from 'lucide-react';
import { VFDState } from '../types';

interface VFDPanelProps {
  data: VFDState;
  onUpdate: (id: string, updates: Partial<VFDState>) => void;
  title: string;
  subTitle?: string;
  disabled?: boolean;
  layout?: 'vertical' | 'horizontal';
  extraControls?: React.ReactNode;
}

export const VFDPanel: React.FC<VFDPanelProps> = ({ 
  data, 
  onUpdate, 
  title, 
  subTitle, 
  disabled = false,
  layout = 'vertical',
  extraControls
}) => {
  const [localSetpoint, setLocalSetpoint] = useState(data.setpoint.toString());

  useEffect(() => {
    setLocalSetpoint(data.setpoint.toString());
  }, [data.setpoint]);

  const handleSetHz = () => {
    const val = parseFloat(localSetpoint);
    if (!isNaN(val) && val >= 0 && val <= 60) {
      onUpdate(data.id, { setpoint: val });
    }
  };

  const handleStart = () => {
    if (data.manualMode) {
      onUpdate(data.id, { status: 'Running' });
    }
  };

  const handleStop = () => {
    if (data.manualMode) {
      onUpdate(data.id, { status: 'Stopped' });
    }
  };

  const toggleMode = () => {
    // Switch between Auto and Manual
    onUpdate(data.id, { manualMode: !data.manualMode });
  };

  const isRunning = data.status === 'Running';
  const isFault = data.status === 'Fault';

  // Calculate percentage for bars
  const freqPercent = (data.frequency / 60) * 100;
  const ampsPercent = (data.current / 20) * 100; // Assuming 20A max

  // --- HORIZONTAL LAYOUT (Toolbar Style) ---
  if (layout === 'horizontal') {
    return (
      <div className={`glass-panel rounded-lg flex items-center px-4 py-2 gap-4 h-full transition-all duration-300 border-l-4 ${isRunning ? 'border-l-scada-success' : 'border-l-transparent bg-white/5'}`}>
        
        {/* 1. Identity */}
        <div className="w-32 shrink-0 flex flex-col justify-center border-r border-white/5 pr-4 relative">
             <div className="flex items-center gap-2 mb-1">
                 <div className={`p-1 rounded shrink-0 ${isRunning ? 'bg-scada-success/10 text-scada-success' : 'bg-scada-dim/10 text-scada-dim'}`}>
                    <Cpu size={14} />
                </div>
                <div className="overflow-hidden">
                    <div className="text-[8px] text-scada-dim font-bold tracking-widest uppercase opacity-80 truncate">{subTitle}</div>
                    <div className="text-xs font-bold text-scada-text leading-none tracking-tight truncate">{title}</div>
                </div>
            </div>
            {/* Status Pill or Extra Controls */}
            {extraControls ? (
               <div className="mt-1">{extraControls}</div>
            ) : (
                <div className={`text-center py-0.5 text-[8px] font-bold rounded-sm border ${
                    isRunning ? 'bg-scada-success/10 border-scada-success/20 text-scada-success' : 
                    isFault ? 'bg-scada-danger/10 border-scada-danger/20 text-scada-danger animate-pulse' : 
                    'bg-scada-dim/10 border-scada-dim/20 text-scada-dim'
                }`}>
                    {data.status.toUpperCase()}
                </div>
            )}
        </div>

        {/* 2. Metrics (Bars) */}
        <div className="flex-1 min-w-[120px] flex flex-col justify-center gap-2">
             {/* Frequency */}
            <div className="flex items-center gap-2">
                <span className="text-[9px] text-scada-dim font-bold w-8 text-right">HZ</span>
                <div className="flex-1 h-1.5 bg-scada-border rounded-full overflow-hidden">
                    <div className={`h-full transition-all duration-500 ease-out rounded-full ${isRunning ? 'bg-scada-accent' : 'bg-scada-dim/30'}`} style={{ width: `${freqPercent}%` }}></div>
                </div>
                <span className="text-[10px] font-mono font-bold text-scada-text w-8 text-right">{data.frequency.toFixed(1)}</span>
            </div>
            {/* Current */}
            <div className="flex items-center gap-2">
                <span className="text-[9px] text-scada-dim font-bold w-8 text-right">AMP</span>
                <div className="flex-1 h-1.5 bg-scada-border rounded-full overflow-hidden">
                    <div className={`h-full transition-all duration-500 ease-out rounded-full ${isRunning ? 'bg-scada-warning' : 'bg-scada-dim/30'}`} style={{ width: `${ampsPercent}%` }}></div>
                </div>
                <span className="text-[10px] font-mono font-bold text-scada-text w-8 text-right">{data.current.toFixed(1)}</span>
            </div>
        </div>
        
        {/* 3. HOA Switch (Auto/Manual) */}
        <div className="shrink-0 flex flex-col items-center gap-1 border-x border-white/5 px-4">
             <span className="text-[8px] font-bold text-scada-dim tracking-wider">MODE</span>
             <button 
                onClick={toggleMode}
                className={`relative w-16 h-6 rounded flex items-center px-1 transition-colors border ${data.manualMode ? 'bg-scada-panel border-scada-accent/50' : 'bg-scada-panel border-scada-dim/30'}`}
             >
                 {/* Sliding Indicator */}
                 <div className={`absolute top-0.5 bottom-0.5 w-7 rounded bg-scada-accent transition-all duration-200 opacity-20 ${data.manualMode ? 'left-[calc(100%-30px)]' : 'left-0.5'}`}></div>
                 
                 <span className={`flex-1 text-[9px] font-bold text-center z-10 transition-colors ${!data.manualMode ? 'text-scada-accent' : 'text-scada-dim'}`}>AUTO</span>
                 <span className={`flex-1 text-[9px] font-bold text-center z-10 transition-colors ${data.manualMode ? 'text-scada-accent' : 'text-scada-dim'}`}>MAN</span>
             </button>
        </div>

        {/* 4. Controls (Start/Stop) - Only Active in Manual */}
        <div className={`shrink-0 flex gap-2 transition-opacity duration-300 ${!data.manualMode ? 'opacity-30 pointer-events-none grayscale' : 'opacity-100'}`}>
            <button 
                onClick={handleStart}
                disabled={disabled || isRunning || !data.manualMode}
                className={`w-9 h-9 rounded flex items-center justify-center transition-all border
                    ${isRunning 
                        ? 'border-transparent bg-scada-success/20 text-scada-success shadow-[0_0_10px_rgba(16,185,129,0.2)]' 
                        : 'bg-scada-panel border-scada-border text-scada-success hover:bg-scada-success/10 hover:border-scada-success/50'}`}
            >
                <Play size={14} fill={isRunning ? "currentColor" : "none"} />
            </button>
            <button 
                onClick={handleStop}
                disabled={disabled || !isRunning || !data.manualMode}
                className={`w-9 h-9 rounded flex items-center justify-center transition-all border
                    ${!isRunning 
                        ? 'border-transparent bg-scada-danger/20 text-scada-danger' 
                        : 'bg-scada-panel border-scada-border text-scada-danger hover:bg-scada-danger/10 hover:border-scada-danger/50'}`}
            >
                <Square size={12} fill="currentColor" />
            </button>
        </div>

      </div>
    );
  }

  // --- VERTICAL LAYOUT (Fallback/Standard) ---
  return (
    <div className={`glass-panel p-0 rounded-lg overflow-hidden flex flex-col h-full transition-all duration-300 border-l-2 ${isRunning ? 'border-l-scada-success' : 'border-l-transparent'}`}>
        <div className="p-4 text-center text-scada-dim">Vertical Layout Not Optimized for New Footer</div>
    </div>
  );
};