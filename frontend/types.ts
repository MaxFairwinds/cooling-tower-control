
export interface VFDState {
  id: string;
  name: string;
  status: 'Running' | 'Stopped' | 'Fault';
  frequency: number; // Hz
  current: number; // Amps
  setpoint: number; // Target Hz (Manual) or Target Temp (Auto) - Overloaded for simplicity in this context, or handled separately
  manualMode: boolean;
}

export interface SystemState {
  isRunning: boolean;
  autoControl: boolean;
  activePump: 'PRIMARY' | 'BACKUP';
  temperature: number; // Treated as Supply Temp (Basin)
  basinLevel?: number; 
  outdoorTemp: number; // Dry Bulb Ambient
  humidity: number; // Relative Humidity %
  heatLoad: number; // Simulated Heat Load % (0-100)
  lastUpdate: Date;
}

export interface ControlSettings {
  pGain: number;
  minFrequency: number;
  maxFrequency: number;
}