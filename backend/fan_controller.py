#!/usr/bin/env python3
"""
Fan PID Controller with Hysteresis
Prevents rapid on/off cycling by using temperature deadband
"""

import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class FanController:
    """
    Fan controller with two modes:
    - MANUAL: Operator sets fixed Hz
    - AUTO: PID control with hysteresis to maintain target temp
    
    Hysteresis logic:
    - Fan OFF: Wait until temp >= (target + hysteresis) before starting
    - Fan ON: Keep running until temp < target
    - This prevents rapid cycling around the setpoint
    
    Example with target=75°F, hysteresis=5°F:
    - Temp rises to 80°F → Fan starts
    - Temp cools to 77°F → Fan still runs (waiting for <75°F)
    - Temp cools to 74°F → Fan stops
    - Temp rises to 79°F → Fan still off (waiting for >=80°F)
    """
    
    def __init__(
        self,
        vfd,
        target_temp: float = 75.0,
        hysteresis: float = 5.0,
        min_hz: float = 20.0,
        max_hz: float = 60.0,
        kp: float = 2.0,
        anti_freeze_temp: float = 45.0
    ):
        """
        Initialize fan controller
        
        Args:
            vfd: VFDController instance
            target_temp: Target basin temperature (°F)
            hysteresis: Temperature deadband (°F)
            min_hz: Minimum fan speed when running (Hz)
            max_hz: Maximum fan speed (Hz)
            kp: Proportional gain for PID
            anti_freeze_temp: Force fan off below this temp
        """
        self.vfd = vfd
        self.target_temp = target_temp
        self.hysteresis = hysteresis
        self.min_hz = min_hz
        self.max_hz = max_hz
        self.kp = kp
        self.anti_freeze_temp = anti_freeze_temp
        
        self.auto_mode = False
        self.manual_setpoint = 0.0  # Hz in manual mode
        self.fan_running = False
        self.last_update = 0
        
        logger.info(
            f"Fan controller initialized: target={target_temp}°F, "
            f"hysteresis={hysteresis}°F, range={min_hz}-{max_hz}Hz"
        )
    
    def enable_auto(self):
        """Enable automatic temperature control"""
        self.auto_mode = True
        logger.info("Fan auto mode ENABLED")
    
    def enable_manual(self):
        """Enable manual frequency control"""
        self.auto_mode = False
        logger.info("Fan manual mode ENABLED")
    
    def set_manual_frequency(self, hz: float):
        """
        Set fan frequency in manual mode
        
        Args:
            hz: Frequency in Hz (0-60)
        """
        if self.auto_mode:
            logger.warning("Cannot set manual frequency in auto mode")
            return False
        
        hz = max(0.0, min(self.max_hz, hz))
        self.manual_setpoint = hz
        
        try:
            self.vfd.set_frequency(hz)
            
            if hz > 0:
                self.vfd.start()
                logger.info(f"Fan manual: {hz:.1f} Hz (STARTING)")
            else:
                self.vfd.stop()
                logger.info("Fan manual: STOPPED")
            
            return True
            
        except Exception as e:
            logger.error(f"Fan manual control error: {e}")
            return False
    
    def update(self, basin_temp: float):
        """
        Update fan control based on basin temperature (auto mode only)
        
        Args:
            basin_temp: Current basin temperature (°F)
        """
        if not self.auto_mode:
            return  # Manual mode, do nothing
        
        # Throttle updates (max 1Hz)
        now = time.time()
        if now - self.last_update < 1.0:
            return
        self.last_update = now
        
        # Anti-freeze protection
        if basin_temp < self.anti_freeze_temp:
            if self.fan_running:
                logger.warning(
                    f"ANTI-FREEZE PROTECTION: Basin temp {basin_temp:.1f}°F "
                    f"< {self.anti_freeze_temp}°F - Stopping fan"
                )
                self._stop_fan()
            return
        
        # Hysteresis logic
        upper_threshold = self.target_temp + self.hysteresis
        lower_threshold = self.target_temp
        
        if not self.fan_running:
            # Fan is OFF - check if we should start
            if basin_temp >= upper_threshold:
                logger.info(
                    f"Fan AUTO START: Temp {basin_temp:.1f}°F >= {upper_threshold:.1f}°F"
                )
                self._start_fan(basin_temp)
        else:
            # Fan is ON - check if we should stop
            if basin_temp < lower_threshold:
                logger.info(
                    f"Fan AUTO STOP: Temp {basin_temp:.1f}°F < {lower_threshold:.1f}°F"
                )
                self._stop_fan()
            else:
                # Fan running, modulate speed based on temperature
                self._modulate_speed(basin_temp)
    
    def _start_fan(self, basin_temp: float):
        """Start fan and set initial frequency"""
        try:
            # Calculate initial frequency based on temp error
            freq = self._calculate_frequency(basin_temp)
            
            self.vfd.set_frequency(freq)
            time.sleep(0.1)
            self.vfd.start()
            
            self.fan_running = True
            logger.info(f"Fan started at {freq:.1f} Hz")
            
        except Exception as e:
            logger.error(f"Fan start error: {e}")
    
    def _stop_fan(self):
        """Stop fan"""
        try:
            self.vfd.stop()
            self.fan_running = False
            logger.info("Fan stopped")
            
        except Exception as e:
            logger.error(f"Fan stop error: {e}")
    
    def _modulate_speed(self, basin_temp: float):
        """
        Adjust fan speed while running (PID control)
        
        The farther above target temp, the faster the fan runs
        """
        try:
            freq = self._calculate_frequency(basin_temp)
            self.vfd.set_frequency(freq)
            
            logger.debug(f"Fan modulating: {freq:.1f} Hz (temp={basin_temp:.1f}°F)")
            
        except Exception as e:
            logger.error(f"Fan modulation error: {e}")
    
    def _calculate_frequency(self, basin_temp: float) -> float:
        """
        Calculate target frequency based on temperature error
        
        Args:
            basin_temp: Current basin temperature
            
        Returns:
            Target frequency (Hz)
        """
        # P-controller: freq = min_hz + (error * kp)
        error = basin_temp - self.target_temp
        
        # When temp is at target, run minimum speed
        # As temp rises, increase speed proportionally
        freq = self.min_hz + (error * self.kp)
        
        # Clamp to valid range
        freq = max(self.min_hz, min(self.max_hz, freq))
        
        return freq
    
    def stop(self):
        """Emergency stop (called on shutdown)"""
        try:
            self.vfd.stop()
            self.fan_running = False
            logger.info("Fan emergency stop")
        except Exception as e:
            logger.error(f"Fan emergency stop error: {e}")
    
    def get_status(self) -> dict:
        """Get current controller status"""
        return {
            'auto_mode': self.auto_mode,
            'manual_setpoint': self.manual_setpoint,
            'fan_running': self.fan_running,
            'target_temp': self.target_temp,
            'hysteresis': self.hysteresis,
            'min_hz': self.min_hz,
            'max_hz': self.max_hz
        }
