"""
Irrigation Controller - Core logic for managing irrigation systems
"""

import json
import os
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any
import schedule
import time
import threading

logger = logging.getLogger(__name__)

class IrrigationController:
    def __init__(self, config_file='/data/irrigation_config.json'):
        self.config_file = config_file
        self.config = self.load_config()
        self.active_waterings = {}
        self.status = {
            'system_active': True,
            'last_watering': None,
            'next_watering': None,
            'active_zones': [],
            'water_usage_today': 0,
            'water_usage_by_room': {},
            'water_usage_by_zone': {},
            'total_plants': 0,
            'active_schedules': 0
        }
        
    def load_config(self) -> Dict:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        
        # Default configuration
        return {
            'rooms': {},
            'zones': {},
            'schedules': {},
            'settings': {
                'dripper_flow_rate': 2.0,  # L/hour per dripper
                'drippers_per_plant': 2,
                'pot_size': 8.0,  # L
                'growing_medium': 'coco'
            }
        }
    
    def save_config(self):
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def get_rooms(self) -> List[Dict]:
        """Get all configured rooms"""
        return list(self.config['rooms'].values())
    
    def create_room(self, room_data: Dict) -> Dict:
        """Create a new room"""
        room_id = str(uuid.uuid4())
        room = {
            'id': room_id,
            'name': room_data['name'],
            'type': room_data.get('type', 'vegetative'),  # vegetative or flowering
            'description': room_data.get('description', ''),
            'zones': [],
            'created_at': datetime.now().isoformat()
        }
        
        self.config['rooms'][room_id] = room
        self.save_config()
        
        logger.info(f"Created room: {room['name']}")
        return {'success': True, 'room': room}
    
    def update_room(self, room_id: str, room_data: Dict) -> Dict:
        """Update room configuration"""
        if room_id not in self.config['rooms']:
            return {'success': False, 'error': 'Room not found'}
        
        room = self.config['rooms'][room_id]
        room.update({
            'name': room_data.get('name', room['name']),
            'type': room_data.get('type', room['type']),
            'description': room_data.get('description', room['description']),
            'updated_at': datetime.now().isoformat()
        })
        
        self.save_config()
        return {'success': True, 'room': room}
    
    def delete_room(self, room_id: str) -> Dict:
        """Delete a room"""
        if room_id not in self.config['rooms']:
            return {'success': False, 'error': 'Room not found'}
        
        # Remove associated zones
        zones_to_remove = []
        for zone_id, zone in self.config['zones'].items():
            if zone['room_id'] == room_id:
                zones_to_remove.append(zone_id)
        
        for zone_id in zones_to_remove:
            del self.config['zones'][zone_id]
        
        del self.config['rooms'][room_id]
        self.save_config()
        
        return {'success': True}
    
    def get_zones(self) -> List[Dict]:
        """Get all irrigation zones"""
        return list(self.config['zones'].values())
    
    def create_zone(self, zone_data: Dict) -> Dict:
        """Create a new irrigation zone"""
        zone_id = str(uuid.uuid4())
        zone = {
            'id': zone_id,
            'name': zone_data['name'],
            'room_id': zone_data['room_id'],
            'plant_count': zone_data.get('plant_count', 1),
            'pump_entity': zone_data.get('pump_entity', ''),
            'solenoid_entity': zone_data.get('solenoid_entity', ''),
            'flow_rate': zone_data.get('flow_rate', 
                self.config['settings']['dripper_flow_rate'] * 
                self.config['settings']['drippers_per_plant'] * 
                zone_data.get('plant_count', 1)
            ),
            'active': True,
            'created_at': datetime.now().isoformat()
        }
        
        self.config['zones'][zone_id] = zone
        
        # Add zone to room
        if zone['room_id'] in self.config['rooms']:
            self.config['rooms'][zone['room_id']]['zones'].append(zone_id)
        
        self.save_config()
        
        logger.info(f"Created zone: {zone['name']}")
        return {'success': True, 'zone': zone}
    
    def get_schedules(self) -> List[Dict]:
        """Get all irrigation schedules"""
        return list(self.config['schedules'].values())
    
    def create_schedule(self, schedule_data: Dict) -> Dict:
        """Create a new irrigation schedule"""
        schedule_id = str(uuid.uuid4())
        schedule_config = {
            'id': schedule_id,
            'name': schedule_data['name'],
            'zone_id': schedule_data['zone_id'],
            'duration': schedule_data['duration'],  # minutes
            'frequency': schedule_data['frequency'],  # daily, weekly, custom
            'times': schedule_data['times'],  # list of times like ["08:00", "20:00"]
            'days': schedule_data.get('days', []),  # for weekly schedules
            'active': True,
            'created_at': datetime.now().isoformat()
        }
        
        self.config['schedules'][schedule_id] = schedule_config
        self.save_config()
        
        # Register with scheduler
        self._register_schedule(schedule_config)
        
        logger.info(f"Created schedule: {schedule_config['name']}")
        return {'success': True, 'schedule': schedule_config}
    
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
        if zone_id not in self.config['zones']:
            logger.error(f"Zone {zone_id} not found")
            return
        
        zone = self.config['zones'][zone_id]
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
        
        # Update total water usage
        self.status['water_usage_today'] += water_used
        
        # Update per-zone water usage
        if zone_id not in self.status['water_usage_by_zone']:
            self.status['water_usage_by_zone'][zone_id] = 0
        self.status['water_usage_by_zone'][zone_id] += water_used
        
        # Update per-room water usage
        room_id = zone['room_id']
        if room_id not in self.status['water_usage_by_room']:
            self.status['water_usage_by_room'][room_id] = 0
        self.status['water_usage_by_room'][room_id] += water_used
        
        # Remove from active waterings
        del self.active_waterings[zone_id]
        
        self.status['last_watering'] = datetime.now().isoformat()
        
        # Save updated status
        self.save_config()
    
    def manual_water(self, zone_id: str, duration: int) -> Dict:
        """Manually trigger watering"""
        if zone_id not in self.config['zones']:
            return {'success': False, 'error': 'Zone not found'}
        
        if zone_id in self.active_waterings:
            return {'success': False, 'error': 'Zone is already watering'}
        
        self._execute_watering(zone_id, duration)
        return {'success': True, 'message': f'Started manual watering for {duration} minutes'}
    
    def get_status(self) -> Dict:
        """Get current system status"""
        self.status['active_zones'] = list(self.active_waterings.keys())
        
        # Update statistics
        self.status['total_plants'] = sum(zone.get('plant_count', 0) for zone in self.config['zones'].values())
        self.status['active_schedules'] = sum(1 for schedule in self.config['schedules'].values() if schedule.get('active', True))
        
        return self.status
    
    def get_detailed_stats(self) -> Dict:
        """Get detailed statistics with room and zone breakdowns"""
        stats = {
            'total_water_today': self.status['water_usage_today'],
            'rooms': [],
            'zones': []
        }
        
        # Room statistics
        for room_id, room in self.config['rooms'].items():
            room_zones = [z for z in self.config['zones'].values() if z['room_id'] == room_id]
            room_plants = sum(z.get('plant_count', 0) for z in room_zones)
            room_water = self.status['water_usage_by_room'].get(room_id, 0)
            
            stats['rooms'].append({
                'id': room_id,
                'name': room['name'],
                'type': room['type'],
                'zones_count': len(room_zones),
                'plants_count': room_plants,
                'water_used_today': round(room_water, 2)
            })
        
        # Zone statistics
        for zone_id, zone in self.config['zones'].items():
            zone_water = self.status['water_usage_by_zone'].get(zone_id, 0)
            room = self.config['rooms'].get(zone['room_id'], {})
            
            stats['zones'].append({
                'id': zone_id,
                'name': zone['name'],
                'room_name': room.get('name', 'Unknown'),
                'plant_count': zone.get('plant_count', 0),
                'flow_rate': zone.get('flow_rate', 0),
                'water_used_today': round(zone_water, 2),
                'active': zone.get('active', True)
            })
        
        return stats