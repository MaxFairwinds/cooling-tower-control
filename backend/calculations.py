#!/usr/bin/env python3
"""
Calculation Service - Derived values for cooling tower system
Calculates heat load, flow rate, return temperature, etc.
"""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class CalculationService:
    """
    Service for calculating derived system values
    
    Uses real sensor data to estimate:
    - Flow rate (GPM) from pump speed
    - Return water temperature from heat load
    - Heat load (kW) using Delta-T method
    - Cooling tower approach
    """
    
    def __init__(self):
        """Initialize calculation service"""
        # Pump curve parameters (for 20HP pump)
        # These are estimates - adjust based on actual pump curves
        self.pump_max_gpm = 80.0  # GPM at 60Hz (20HP ≈ 80 GPM)
        self.pump_min_gpm = 0.0    # GPM at 0Hz
        
        # Heat transfer constants
        self.water_specific_heat = 500  # BTU/(hr·°F·GPM) - standard for water
        self.btu_to_kw = 3412.14        # BTU/hr to kW conversion
        
        logger.info("Calculation service initialized")
    
    def calculate(
        self,
        basin_temp: float,
        pump_hz: float,
        outdoor_temp: float,
        humidity: float
    ) -> Dict:
        """
        Calculate all derived values
        
        Args:
            basin_temp: Basin water temperature (°F)
            pump_hz: Pump frequency (Hz)
            outdoor_temp: Outdoor dry bulb temperature (°F)
            humidity: Relative humidity (%)
            
        Returns:
            Dictionary with calculated values
        """
        # 1. Calculate flow rate from pump speed
        gpm = self._calculate_gpm(pump_hz)
        
        # 2. Estimate return temperature based on flow and load
        return_temp = self._calculate_return_temp(basin_temp, pump_hz)
        
        # 3. Calculate heat load using Delta-T method
        heat_load_kw = self._calculate_heat_load(gpm, basin_temp, return_temp)
        
        # 4. Calculate wet bulb and cooling tower approach
        wet_bulb = self._calculate_wet_bulb(outdoor_temp, humidity)
        approach = basin_temp - wet_bulb
        
        return {
            'gpm': gpm,
            'return_temp_f': return_temp,
            'heat_load_kw': heat_load_kw,
            'wet_bulb_f': wet_bulb,
            'approach_f': approach
        }
    
    def _calculate_gpm(self, pump_hz: float) -> float:
        """
        Estimate flow rate from pump frequency
        
        Assumes linear relationship between Hz and GPM
        (Close enough for centrifugal pumps in normal operating range)
        
        Args:
            pump_hz: Pump frequency (0-60 Hz)
            
        Returns:
            Flow rate (GPM)
        """
        if pump_hz <= 0:
            return 0.0
        
        # Linear interpolation: GPM = (Hz / 60) * max_GPM
        # 20HP pump at 60Hz ≈ 80 GPM
        # At 45Hz (fixed operating point) ≈ 60 GPM
        # At 30Hz ≈ 40 GPM
        gpm = (pump_hz / 60.0) * self.pump_max_gpm
        
        return max(0.0, gpm)
    
    def _calculate_return_temp(self, basin_temp: float, pump_hz: float) -> float:
        """
        Estimate return water temperature
        
        The return temp is hotter than basin temp due to heat rejection
        from the building. We estimate this based on pump speed (proxy for load).
        
        Typical water-source heat pump systems:
        - Low load (winter): 5-10°F rise
        - High load (summer): 15-25°F rise
        
        Args:
            basin_temp: Basin supply temperature (°F)
            pump_hz: Pump frequency (Hz) - proxy for building load
            
        Returns:
            Estimated return temperature (°F)
        """
        if pump_hz <= 0:
            # No flow, no temperature rise
            return basin_temp
        
        # Estimate load factor from pump speed
        # Pump at 45Hz (fixed) = ~75% capacity = moderate load
        # Use this to estimate temperature rise
        load_factor = pump_hz / 60.0  # 0 to 1
        
        # Temperature rise scales with load
        # Conservative estimate: 20°F rise at full load
        # This matches user's estimate of "20F" delta
        max_delta_t = 20.0  # °F at full load (60Hz)
        delta_t = max_delta_t * load_factor
        
        return basin_temp + delta_t
    
    def _calculate_heat_load(
        self,
        gpm: float,
        supply_temp: float,
        return_temp: float
    ) -> float:
        """
        Calculate heat load using Delta-T method
        
        Formula: Q = GPM × 500 × ΔT (BTU/hr)
        Where:
        - GPM = flow rate
        - 500 = water specific heat constant
        - ΔT = temperature rise (return - supply)
        
        Args:
            gpm: Flow rate (GPM)
            supply_temp: Supply water temperature (°F)
            return_temp: Return water temperature (°F)
            
        Returns:
            Heat load (kW)
        """
        if gpm <= 0:
            return 0.0
        
        delta_t = return_temp - supply_temp
        
        # Heat load in BTU/hr
        heat_load_btu = gpm * self.water_specific_heat * delta_t
        
        # Convert to kW
        heat_load_kw = heat_load_btu / self.btu_to_kw
        
        # Clamp to positive values (can't have negative heat load)
        return max(0.0, heat_load_kw)
    
    def _calculate_wet_bulb(self, dry_bulb_f: float, relative_humidity: float) -> float:
        """
        Calculate wet bulb temperature
        
        Uses simplified approximation:
        WB ≈ DB - ((100 - RH) * 0.3)
        
        This is accurate enough for HVAC applications (±1°F)
        
        Args:
            dry_bulb_f: Dry bulb temperature (°F)
            relative_humidity: Relative humidity (%)
            
        Returns:
            Wet bulb temperature (°F)
        """
        return dry_bulb_f - ((100 - relative_humidity) * 0.30)
    
    def calculate_approach(self, basin_temp: float, wet_bulb_temp: float) -> float:
        """
        Calculate cooling tower approach
        
        Approach is the difference between basin temp and wet bulb temp.
        Lower is better (more efficient tower).
        
        Typical approaches:
        - Excellent: 5-7°F
        - Good: 7-10°F
        - Acceptable: 10-15°F
        - Poor: >15°F
        
        Args:
            basin_temp: Basin water temperature (°F)
            wet_bulb_temp: Outdoor wet bulb temperature (°F)
            
        Returns:
            Approach temperature (°F)
        """
        return basin_temp - wet_bulb_temp
