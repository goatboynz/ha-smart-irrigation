"""
Irrigation Controller - Core logic for managing irrigation systems
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import schedule
import time
import threading
from database import IrrigationDatabase

logger = logging.getLogger(__name__)

class IrrigationController:
    def __init__(self):
        self.db = IrrigationDatabase()
        self.active_waterings = {}
        logger.info("Irrigation controller initialized with database")
    
    def get_rooms(self) -> List[Dict]:
        """Get all configured rooms"""
        return self.db.get_rooms()
    
    def create_room(self, room_data: Dict) -> Dict:
        """Create a new room"""
        logger.info(f"Creating room with data: {room_data}")
        
        name = room_data.get('name', '')
        room_type = room_data.get('type', 'vegetative')
        description = room_data.get('description', '')
        
        if not name:
            return {'success': False, 'error': 'Room name is required'}
        
        return self.db.create_room(name, room_type, description)
    
    def update_room(self, room_id: str, room_data: Dict) -> Dict:
        """Update room configuration"""
        name = room_data.get('name', '')
        room_type = room_data.get('type', 'vegetative')
        description = room_data.get('description', '')
        
        return self.db.update_room(room_id, name, room_type, description)
    
    def delete_room(self, room_id: str) -> Dict:
        """Delete a room"""
        return self.db.delete_room(room_id)
    
    def get_zones(self) -> List[Dict]:
        """Get all irrigation zones"""
        return self.db.get_zones()
    
    def create_zone(self, zone_data: Dict) -> Dict:
        """Create a new irrigation zone"""
        name = zone_data.get('name', '')
        room_id = zone_data.get('room_id', '')
        plant_count = zone_data.get('plant_count', 1)
        pump_entity = zone_data.get('pump_entity', '')
        solenoid_entity = zone_data.get('solenoid_entity', '')
        
        if not name or not room_id:
            return {'success': False, 'error': 'Zone name and room are required'}
        
        return self.db.create_zone(name, room_id, plant_count, pump_entity, solenoid_entity)
    
    def get_schedules(self) -> List[Dict]:
        """Get all irrigation schedules"""
        return self.db.get_schedules()
    
    def create_schedule(self, schedule_data: Dict) -> Dict:
        """Create a new irrigation schedule"""
        name = schedule_data.get('name', '')
        zone_id = schedule_data.get('zone_id', '')
        duration = schedule_data.get('duration', 5)
        frequency = schedule_data.get('frequency', 'daily')
        times = schedule_data.get('times', [])
        days = schedule_data.get('days', [])
        
        if not name or not zone_id or not times:
            return {'success': False, 'error': 'Schedule name, zone, and times are required'}
        
        result = self.db.create_schedule(name, zone_id, duration, frequency, times, days)
        
        if result['success']:
            # Register with scheduler
            self._register_schedule(result['schedule'])
        
        return result
    
    def _register_schedule(self, schedule_config: Dict):
        """Register schedule with the scheduler"""
        zone_id = schedule_config['zone_id']
        duration = schedule_config['duration']
        
        for time_str in schedule_config['times']:
            if schedule_config['frequency'] == 'daily':
                schedule.every().day.at(time_str).do(
                    self._execute_watering, zone_id, duration
                )
            elif schedule_config['frequency'] == 'weekly':
                for day in schedule_config['days']:
                    getattr(schedule.every(), day.lower()).at(time_str).do(
                        self._execute_watering, zone_id, duration
                    )
    
    def _execute_watering(self, zone_id: str, duration: int):
        """Execute watering for a zone"""
        zones = self.db.get_zones()
        zone = next((z for z in zones if z['id'] == zone_id), None)
        
        if not zone:
            logger.error(f"Zone {zone_id} not found")
            return
        
        if not zone['active']:
            logger.info(f"Zone {zone['name']} is inactive, skipping watering")
            return
        
        logger.info(f"Starting watering for zone {zone['name']} for {duration} minutes")
        
        # Start watering
        self.active_waterings[zone_id] = {
            'start_time': datetime.now(),
            'duration': duration,
            'zone': zone
        }
        
        # Turn on pump and solenoid via Home Assistant
        from ha_integration import HomeAssistantIntegration
        ha = HomeAssistantIntegration()
        
        if zone['pump_entity']:
            ha.turn_on_switch(zone['pump_entity'])
        if zone['solenoid_entity']:
            ha.turn_on_switch(zone['solenoid_entity'])
        
        # Schedule stop
        def stop_watering():
            time.sleep(duration * 60)  # Convert to seconds
            self._stop_watering(zone_id)
        
        threading.Thread(target=stop_watering, daemon=True).start()
    
    def _stop_watering(self, zone_id: str):
        """Stop watering for a zone"""
        if zone_id not in self.active_waterings:
            return
        
        watering = self.active_waterings[zone_id]
        zone = watering['zone']
        
        logger.info(f"Stopping watering for zone {zone['name']}")
        
        # Turn off pump and solenoid
        from ha_integration import HomeAssistantIntegration
        ha = HomeAssistantIntegration()
        
        if zone['pump_entity']:
            ha.turn_off_switch(zone['pump_entity'])
        if zone['solenoid_entity']:
            ha.turn_off_switch(zone['solenoid_entity'])
        
        # Calculate water usage
        duration_hours = watering['duration'] / 60
        water_used = zone['flow_rate'] * duration_hours
        
        # Log water usage to database
        self.db.log_water_usage(zone_id, zone['room_id'], water_used, watering['duration'])
        
        # Remove from active waterings
        del self.active_waterings[zone_id]
        
        logger.info(f"Watering completed for zone {zone['name']}, used {water_used:.2f}L")
    
    def manual_water(self, zone_id: str, duration: int) -> Dict:
        """Manually trigger watering"""
        zones = self.db.get_zones()
        zone = next((z for z in zones if z['id'] == zone_id), None)
        
        if not zone:
            return {'success': False, 'error': 'Zone not found'}
        
        if zone_id in self.active_waterings:
            return {'success': False, 'error': 'Zone is already watering'}
        
        self._execute_watering(zone_id, duration)
        return {'success': True, 'message': f'Started manual watering for {duration} minutes'}
    
    def get_status(self) -> Dict:
        """Get current system status"""
        status = self.db.get_system_status()
        status['active_zones'] = list(self.active_waterings.keys())
        return status
    
    def get_detailed_stats(self) -> Dict:
        """Get detailed statistics with room and zone breakdowns"""
        return self.db.get_water_usage_stats()