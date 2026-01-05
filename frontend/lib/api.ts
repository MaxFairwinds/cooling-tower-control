/**
 * API Client for Cooling Tower SCADA Backend
 * All control actions go through REST API
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'APIError';
  }
}

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new APIError(response.status, `API error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof APIError) throw error;
    throw new Error(`Network error: ${error instanceof Error ? error.message : 'Unknown'}`);
  }
}

export const api = {
  // Fan control
  fan: {
    setMode: (mode: 'manual' | 'auto') =>
      request('/api/fan/mode', {
        method: 'POST',
        body: JSON.stringify({ mode }),
      }),

    setFrequency: (hz: number) =>
      request('/api/fan/setpoint', {
        method: 'POST',
        body: JSON.stringify({ hz }),
      }),

    setAutoConfig: (targetTemp: number, hysteresis: number) =>
      request('/api/fan/auto_config', {
        method: 'POST',
        body: JSON.stringify({ target_temp: targetTemp, hysteresis }),
      }),
  },

  // Pump control
  pump: {
    setFrequency: (hz: number) =>
      request('/api/pump/frequency', {
        method: 'POST',
        body: JSON.stringify({ hz }),
      }),

    start: () =>
      request('/api/pump/start', {
        method: 'POST',
      }),

    stop: () =>
      request('/api/pump/stop', {
        method: 'POST',
      }),

    switch: () =>
      request('/api/pump/switch', {
        method: 'POST',
      }),
  },

  // Status endpoints (for fallback polling if WebSocket fails)
  status: {
    getFull: () => request('/api/status'),
    getSensors: () => request('/api/sensors'),
    getVFDs: () => request('/api/vfds'),
    getWeather: () => request('/api/weather'),
  },

  // Health check
  health: () => request('/api/health'),
};

export default api;
