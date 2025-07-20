"""
Home Assistant Integration
Handles communication with Home Assistant API
"""

import os
import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class HomeAssistantIntegration:
    def __init__(self):
        self.ha_url = os.getenv('SUPERVISOR_TOKEN') and 'http://supervisor/core' or 'http://homeassistant:8123'
        self.token = self._get_token()
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
    
    def _get_token(self) -> str:
        """Get Home Assistant access token"""
        # Try supervisor token first (for addon)
        supervisor_token = os.getenv('SUPERVISOR_TOKEN')
        if supervisor_token:
            return supervisor_token
        
        # Fallback to long-lived access token
        token_file = '/data/ha_token.txt'
        if os.path.exists(token_file):
            with open(token_file, 'r') as f:
                return f.read().strip()
        
        logger.warning("No Home Assistant token found. Please configure authentication.")
        return ""
    
    def turn_on_switch(self, entity_id: str) -> bool:
        """Turn on a Home Assistant switch"""
        try:
            url = f"{self.ha_url}/api/services/switch/turn_on"
            data = {"entity_id": entity_id}
            
            response = requests.post(url, json=data, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Turned on switch: {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to turn on switch {entity_id}: {e}")
            return False
    
    def turn_off_switch(self, entity_id: str) -> bool:
        """Turn off a Home Assistant switch"""
        try:
            url = f"{self.ha_url}/api/services/switch/turn_off"
            data = {"entity_id": entity_id}
            
            response = requests.post(url, json=data, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Turned off switch: {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to turn off switch {entity_id}: {e}")
            return False
    
    def get_switch_state(self, entity_id: str) -> Dict[str, Any]:
        """Get the state of a Home Assistant switch"""
        try:
            url = f"{self.ha_url}/api/states/{entity_id}"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get switch state {entity_id}: {e}")
            return {}
    
    def get_all_switches(self) -> list:
        """Get all available switches from Home Assistant"""
        try:
            url = f"{self.ha_url}/api/states"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            states = response.json()
            switches = [
                state for state in states 
                if state['entity_id'].startswith('switch.')
            ]
            
            return switches
            
        except Exception as e:
            logger.error(f"Failed to get switches: {e}")
            return []
    
    def create_sensor(self, sensor_id: str, name: str, state: Any, attributes: Dict = None) -> bool:
        """Create or update a sensor in Home Assistant"""
        try:
            url = f"{self.ha_url}/api/states/sensor.{sensor_id}"
            data = {
                "state": state,
                "attributes": {
                    "friendly_name": name,
                    "unit_of_measurement": attributes.get("unit") if attributes else None,
                    "device_class": attributes.get("device_class") if attributes else None,
                    **(attributes or {})
                }
            }
            
            response = requests.post(url, json=data, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Created/updated sensor: sensor.{sensor_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create sensor {sensor_id}: {e}")
            return False