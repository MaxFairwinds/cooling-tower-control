#!/usr/bin/env python3
"""
Weather Service - Fetches outdoor temperature and humidity from Weather.gov API
Free, no API key required, official NOAA data
"""

import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class WeatherService:
    """
    Weather data service using Weather.gov API
    
    API Documentation: https://www.weather.gov/documentation/services-web-api
    
    For Vancouver, WA (ZIP 98664):
    Latitude: 45.6387° N
    Longitude: -122.6615° W
    """
    
    def __init__(self, zip_code: str = "98664"):
        """
        Initialize weather service
        
        Args:
            zip_code: ZIP code for location (default: Vancouver, WA)
        """
        self.zip_code = zip_code
        
        # Coordinates for Vancouver, WA
        # In production, you might want to geocode the ZIP
        self.lat = 45.6387
        self.lon = -122.6615
        
        self.data = {
            'temp_f': 0.0,
            'humidity': 0.0,
            'wet_bulb_f': 0.0,
            'last_update': '',
            'status': 'offline'
        }
        
        self.station_url: Optional[str] = None
        self.last_successful_update: Optional[datetime] = None
        
        logger.info(f"Weather service initialized for {zip_code} ({self.lat}, {self.lon})")
    
    async def update(self):
        """Fetch latest weather data"""
        try:
            # If we don't have a station URL, get it first
            if not self.station_url:
                await self._initialize_station()
            
            # Fetch current observations
            response = requests.get(
                self.station_url,
                headers={'User-Agent': 'CoolingTowerSCADA/2.0'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self._parse_weather_data(data)
                self.last_successful_update = datetime.now()
                logger.info(
                    f"Weather updated: {self.data['temp_f']:.1f}°F, "
                    f"{self.data['humidity']:.0f}% RH"
                )
            else:
                logger.error(f"Weather API error: {response.status_code}")
                self._mark_stale()
                
        except Exception as e:
            logger.error(f"Weather update failed: {e}")
            self._mark_stale()
    
    async def _initialize_station(self):
        """Get nearest weather station for our location"""
        try:
            # Step 1: Get grid point for our coordinates
            points_url = f"https://api.weather.gov/points/{self.lat},{self.lon}"
            response = requests.get(
                points_url,
                headers={'User-Agent': 'CoolingTowerSCADA/2.0'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                # Get the observation station URL
                stations_url = data['properties']['observationStations']
                
                # Step 2: Get list of stations
                response = requests.get(
                    stations_url,
                    headers={'User-Agent': 'CoolingTowerSCADA/2.0'},
                    timeout=10
                )
                
                if response.status_code == 200:
                    stations = response.json()
                    # Use the first (nearest) station
                    if stations['features']:
                        station_id = stations['features'][0]['properties']['stationIdentifier']
                        self.station_url = f"https://api.weather.gov/stations/{station_id}/observations/latest"
                        logger.info(f"Using weather station: {station_id}")
                    else:
                        logger.error("No weather stations found")
                else:
                    logger.error(f"Failed to get stations: {response.status_code}")
            else:
                logger.error(f"Failed to get grid point: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Weather station initialization failed: {e}")
    
    def _parse_weather_data(self, data: dict):
        """Parse weather data from API response"""
        try:
            props = data['properties']
            
            # Temperature (convert from Celsius to Fahrenheit)
            temp_c = props['temperature']['value']
            if temp_c is not None:
                temp_f = (temp_c * 9/5) + 32
            else:
                temp_f = 0.0
            
            # Relative humidity
            humidity = props['relativeHumidity']['value']
            if humidity is None:
                humidity = 0.0
            
            # Calculate wet bulb temperature
            # Using simplified approximation:
            # WB ≈ DB - ((100 - RH) * 0.3)
            wet_bulb_f = temp_f - ((100 - humidity) * 0.30)
            
            # Update data
            self.data = {
                'temp_f': temp_f,
                'humidity': humidity,
                'wet_bulb_f': wet_bulb_f,
                'last_update': datetime.now().isoformat(),
                'status': 'online'
            }
            
        except Exception as e:
            logger.error(f"Failed to parse weather data: {e}")
            self._mark_stale()
    
    def _mark_stale(self):
        """Mark data as stale if update fails"""
        if self.last_successful_update:
            age = datetime.now() - self.last_successful_update
            if age > timedelta(hours=1):
                self.data['status'] = 'stale'
            else:
                self.data['status'] = 'online'  # Recent enough
        else:
            self.data['status'] = 'offline'
    
    def get_data(self) -> Dict:
        """Get current weather data"""
        # Check if data is stale
        if self.last_successful_update:
            age = datetime.now() - self.last_successful_update
            if age > timedelta(hours=1):
                self.data['status'] = 'stale'
        
        return self.data.copy()
    
    def calculate_wet_bulb(self, dry_bulb_f: float, relative_humidity: float) -> float:
        """
        Calculate wet bulb temperature using simplified approximation
        
        This is the Stull formula approximation:
        Tw = T * atan[0.151977 * (RH% + 8.313659)^(1/2)] + ...
        
        But we use a simpler linear approximation for speed:
        WB ≈ DB - ((100 - RH) * 0.3)
        
        Args:
            dry_bulb_f: Dry bulb temperature (°F)
            relative_humidity: Relative humidity (%)
            
        Returns:
            Wet bulb temperature (°F)
        """
        return dry_bulb_f - ((100 - relative_humidity) * 0.30)
