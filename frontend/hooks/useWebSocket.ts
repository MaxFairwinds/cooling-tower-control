import { useState, useEffect, useCallback, useRef } from 'react';

export interface SystemData {
  sensors: {
    pressure_psi: number;
    basin_temp_f: number;
    timestamp: string;
    status: 'online' | 'offline';
  };
  fan: {
    state: 'Running' | 'Stopped' | 'Fault' | 'NoComm';
    frequency: number;
    current: number;
    fault_code: number;
  };
  pump_primary: {
    state: 'Running' | 'Stopped' | 'Fault' | 'NoComm';
    frequency: number;
    current: number;
    fault_code: number;
  };
  pump_backup: {
    state: 'Running' | 'Stopped' | 'Fault' | 'NoComm';
    frequency: number;
    current: number;
    fault_code: number;
  };
  active_pump: 'primary' | 'backup' | 'failed';
  weather: {
    outdoor_temp_f: number;
    humidity_pct: number;
    wet_bulb_f: number;
    last_update: string;
    status: 'online' | 'stale' | 'offline' | 'mock';
  };
  calculated: {
    return_temp_f: number;
    heat_load_kw: number;
    gpm: number;
    approach_f: number;
  };
  fan_auto_mode: boolean;
  fan_setpoint: number;
}

interface UseWebSocketResult {
  data: SystemData | null;
  isConnected: boolean;
  error: string | null;
  reconnect: () => void;
}

const RECONNECT_INTERVAL = 3000; // 3 seconds

export function useWebSocket(): UseWebSocketResult {
  const [data, setData] = useState<SystemData | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const shouldReconnectRef = useRef(true);

  const connect = useCallback(() => {
    try {
      const wsUrl = import.meta.env.VITE_WS_URL || `ws://${window.location.hostname}/ws`;
      console.log(`[WebSocket] Connecting to ${wsUrl}...`);
      
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('[WebSocket] Connected');
        setIsConnected(true);
        setError(null);
        
        // Clear any pending reconnect
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
      };

      ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data) as SystemData;
          setData(parsed);
        } catch (err) {
          console.error('[WebSocket] Failed to parse message:', err);
        }
      };

      ws.onerror = (event) => {
        console.error('[WebSocket] Error:', event);
        setError('Connection error');
      };

      ws.onclose = () => {
        console.log('[WebSocket] Disconnected');
        setIsConnected(false);
        wsRef.current = null;

        // Auto-reconnect if enabled
        if (shouldReconnectRef.current) {
          console.log(`[WebSocket] Reconnecting in ${RECONNECT_INTERVAL}ms...`);
          reconnectTimeoutRef.current = window.setTimeout(() => {
            connect();
          }, RECONNECT_INTERVAL);
        }
      };

    } catch (err) {
      console.error('[WebSocket] Connection failed:', err);
      setError(err instanceof Error ? err.message : 'Connection failed');
    }
  }, []);

  const disconnect = useCallback(() => {
    shouldReconnectRef.current = false;
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setIsConnected(false);
  }, []);

  const reconnect = useCallback(() => {
    disconnect();
    shouldReconnectRef.current = true;
    connect();
  }, [connect, disconnect]);

  // Connect on mount, disconnect on unmount
  useEffect(() => {
    connect();
    
    return () => {
      disconnect();
    };
  }, [connect, disconnect]);

  return {
    data,
    isConnected,
    error,
    reconnect
  };
}
