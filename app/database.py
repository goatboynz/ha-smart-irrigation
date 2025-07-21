"""
Database module for Smart Irrigation Controller
Uses SQLite for reliable data storage
"""

import sqlite3
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

logger = logging.getLogger(__name__)

class IrrigationDatabase:
    def __init__(self, db_path='/data/irrigation.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('PRAGMA foreign_keys = ON')
                
                # Rooms table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS rooms (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        type TEXT NOT NULL,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Zones table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS zones (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        room_id TEXT NOT NULL,
                        plant_count INTEGER DEFAULT 1,
                        pump_entity TEXT,
                        solenoid_entity TEXT,
                        flow_rate REAL DEFAULT 4.0,
                        active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (room_id) REFERENCES rooms (id) ON DELETE CASCADE
                    )
                ''')
                
                # Schedules table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS schedules (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        zone_id TEXT NOT NULL,
                        duration INTEGER NOT NULL,
                        frequency TEXT NOT NULL,
                        times TEXT NOT NULL,
                        days TEXT,
                        active BOOLEAN DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (zone_id) REFERENCES zones (id) ON DELETE CASCADE
                    )
                ''')
                
                # Water usage log table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS water_usage (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        zone_id TEXT NOT NULL,
                        room_id TEXT NOT NULL,
                        amount REAL NOT NULL,
                        duration INTEGER NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (zone_id) REFERENCES zones (id),
                        FOREIGN KEY (room_id) REFERENCES rooms (id)
                    )
                ''')
                
                # System settings table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
        return conn
    
    # Room operations
    def create_room(self, name: str, room_type: str, description: str = '') -> Dict:
        """Create a new room"""
        try:
            room_id = str(uuid.uuid4())
            
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT INTO rooms (id, name, type, description)
                    VALUES (?, ?, ?, ?)
                ''', (room_id, name, room_type, description))
                
                conn.commit()
                
                # Get the created room
                room = conn.execute('''
                    SELECT * FROM rooms WHERE id = ?
                ''', (room_id,)).fetchone()
                
                logger.info(f"Created room: {name}")
                return {
                    'success': True,
                    'room': {
                        'id': room['id'],
                        'name': room['name'],
                        'type': room['type'],
                        'description': room['description'],
                        'created_at': room['created_at']
                    }
                }
                
        except Exception as e:
            logger.error(f"Error creating room: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_rooms(self) -> List[Dict]:
        """Get all rooms"""
        try:
            with self.get_connection() as conn:
                rooms = conn.execute('''
                    SELECT r.*, COUNT(z.id) as zone_count
                    FROM rooms r
                    LEFT JOIN zones z ON r.id = z.room_id
                    GROUP BY r.id
                    ORDER BY r.created_at
                ''').fetchall()
                
                return [dict(room) for room in rooms]
                
        except Exception as e:
            logger.error(f"Error getting rooms: {e}")
            return []
    
    def update_room(self, room_id: str, name: str, room_type: str, description: str = '') -> Dict:
        """Update a room"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    UPDATE rooms 
                    SET name = ?, type = ?, description = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (name, room_type, description, room_id))
                
                if conn.total_changes == 0:
                    return {'success': False, 'error': 'Room not found'}
                
                conn.commit()
                
                # Get updated room
                room = conn.execute('SELECT * FROM rooms WHERE id = ?', (room_id,)).fetchone()
                
                return {
                    'success': True,
                    'room': dict(room)
                }
                
        except Exception as e:
            logger.error(f"Error updating room: {e}")
            return {'success': False, 'error': str(e)}
    
    def delete_room(self, room_id: str) -> Dict:
        """Delete a room and all its zones"""
        try:
            with self.get_connection() as conn:
                # Check if room exists
                room = conn.execute('SELECT * FROM rooms WHERE id = ?', (room_id,)).fetchone()
                if not room:
                    return {'success': False, 'error': 'Room not found'}
                
                # Delete room (zones will be deleted by CASCADE)
                conn.execute('DELETE FROM rooms WHERE id = ?', (room_id,))
                conn.commit()
                
                logger.info(f"Deleted room: {room['name']}")
                return {'success': True}
                
        except Exception as e:
            logger.error(f"Error deleting room: {e}")
            return {'success': False, 'error': str(e)}
    
    # Zone operations
    def create_zone(self, name: str, room_id: str, plant_count: int = 1, 
                   pump_entity: str = '', solenoid_entity: str = '') -> Dict:
        """Create a new zone"""
        try:
            zone_id = str(uuid.uuid4())
            flow_rate = 2.0 * 2 * plant_count  # 2L/hour per dripper, 2 drippers per plant
            
            with self.get_connection() as conn:
                # Check if room exists
                room = conn.execute('SELECT * FROM rooms WHERE id = ?', (room_id,)).fetchone()
                if not room:
                    return {'success': False, 'error': 'Room not found'}
                
                conn.execute('''
                    INSERT INTO zones (id, name, room_id, plant_count, pump_entity, solenoid_entity, flow_rate)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (zone_id, name, room_id, plant_count, pump_entity, solenoid_entity, flow_rate))
                
                conn.commit()
                
                # Get the created zone
                zone = conn.execute('''
                    SELECT z.*, r.name as room_name
                    FROM zones z
                    JOIN rooms r ON z.room_id = r.id
                    WHERE z.id = ?
                ''', (zone_id,)).fetchone()
                
                logger.info(f"Created zone: {name}")
                return {
                    'success': True,
                    'zone': dict(zone)
                }
                
        except Exception as e:
            logger.error(f"Error creating zone: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_zones(self) -> List[Dict]:
        """Get all zones with room information"""
        try:
            with self.get_connection() as conn:
                zones = conn.execute('''
                    SELECT z.*, r.name as room_name, r.type as room_type
                    FROM zones z
                    JOIN rooms r ON z.room_id = r.id
                    ORDER BY r.name, z.name
                ''').fetchall()
                
                return [dict(zone) for zone in zones]
                
        except Exception as e:
            logger.error(f"Error getting zones: {e}")
            return []
    
    # Schedule operations
    def create_schedule(self, name: str, zone_id: str, duration: int, 
                       frequency: str, times: List[str], days: List[str] = None) -> Dict:
        """Create a new schedule"""
        try:
            schedule_id = str(uuid.uuid4())
            times_json = json.dumps(times)
            days_json = json.dumps(days) if days else None
            
            with self.get_connection() as conn:
                # Check if zone exists
                zone = conn.execute('SELECT * FROM zones WHERE id = ?', (zone_id,)).fetchone()
                if not zone:
                    return {'success': False, 'error': 'Zone not found'}
                
                conn.execute('''
                    INSERT INTO schedules (id, name, zone_id, duration, frequency, times, days)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (schedule_id, name, zone_id, duration, frequency, times_json, days_json))
                
                conn.commit()
                
                # Get the created schedule
                schedule = conn.execute('''
                    SELECT s.*, z.name as zone_name, r.name as room_name
                    FROM schedules s
                    JOIN zones z ON s.zone_id = z.id
                    JOIN rooms r ON z.room_id = r.id
                    WHERE s.id = ?
                ''', (schedule_id,)).fetchone()
                
                schedule_dict = dict(schedule)
                schedule_dict['times'] = json.loads(schedule_dict['times'])
                if schedule_dict['days']:
                    schedule_dict['days'] = json.loads(schedule_dict['days'])
                
                logger.info(f"Created schedule: {name}")
                return {
                    'success': True,
                    'schedule': schedule_dict
                }
                
        except Exception as e:
            logger.error(f"Error creating schedule: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_schedules(self) -> List[Dict]:
        """Get all schedules"""
        try:
            with self.get_connection() as conn:
                schedules = conn.execute('''
                    SELECT s.*, z.name as zone_name, r.name as room_name
                    FROM schedules s
                    JOIN zones z ON s.zone_id = z.id
                    JOIN rooms r ON z.room_id = r.id
                    ORDER BY s.name
                ''').fetchall()
                
                result = []
                for schedule in schedules:
                    schedule_dict = dict(schedule)
                    schedule_dict['times'] = json.loads(schedule_dict['times'])
                    if schedule_dict['days']:
                        schedule_dict['days'] = json.loads(schedule_dict['days'])
                    result.append(schedule_dict)
                
                return result
                
        except Exception as e:
            logger.error(f"Error getting schedules: {e}")
            return []
    
    # Water usage tracking
    def log_water_usage(self, zone_id: str, room_id: str, amount: float, duration: int):
        """Log water usage"""
        try:
            with self.get_connection() as conn:
                conn.execute('''
                    INSERT INTO water_usage (zone_id, room_id, amount, duration)
                    VALUES (?, ?, ?, ?)
                ''', (zone_id, room_id, amount, duration))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error logging water usage: {e}")
    
    def get_water_usage_stats(self) -> Dict:
        """Get water usage statistics"""
        try:
            with self.get_connection() as conn:
                # Total usage today
                total_today = conn.execute('''
                    SELECT COALESCE(SUM(amount), 0) as total
                    FROM water_usage
                    WHERE DATE(timestamp) = DATE('now')
                ''').fetchone()['total']
                
                # Usage by room today
                room_usage = conn.execute('''
                    SELECT r.id, r.name, r.type, COALESCE(SUM(w.amount), 0) as water_used
                    FROM rooms r
                    LEFT JOIN water_usage w ON r.id = w.room_id AND DATE(w.timestamp) = DATE('now')
                    GROUP BY r.id, r.name, r.type
                    ORDER BY r.name
                ''').fetchall()
                
                # Usage by zone today
                zone_usage = conn.execute('''
                    SELECT z.id, z.name, r.name as room_name, z.plant_count, 
                           COALESCE(SUM(w.amount), 0) as water_used
                    FROM zones z
                    JOIN rooms r ON z.room_id = r.id
                    LEFT JOIN water_usage w ON z.id = w.zone_id AND DATE(w.timestamp) = DATE('now')
                    GROUP BY z.id, z.name, r.name, z.plant_count
                    ORDER BY r.name, z.name
                ''').fetchall()
                
                return {
                    'total_water_today': float(total_today),
                    'rooms': [dict(row) for row in room_usage],
                    'zones': [dict(row) for row in zone_usage]
                }
                
        except Exception as e:
            logger.error(f"Error getting water usage stats: {e}")
            return {'total_water_today': 0, 'rooms': [], 'zones': []}
    
    def get_system_status(self) -> Dict:
        """Get system status"""
        try:
            with self.get_connection() as conn:
                # Count totals
                room_count = conn.execute('SELECT COUNT(*) as count FROM rooms').fetchone()['count']
                zone_count = conn.execute('SELECT COUNT(*) as count FROM zones').fetchone()['count']
                schedule_count = conn.execute('SELECT COUNT(*) as count FROM schedules WHERE active = 1').fetchone()['count']
                plant_count = conn.execute('SELECT COALESCE(SUM(plant_count), 0) as count FROM zones').fetchone()['count']
                
                # Water usage today
                water_today = conn.execute('''
                    SELECT COALESCE(SUM(amount), 0) as total
                    FROM water_usage
                    WHERE DATE(timestamp) = DATE('now')
                ''').fetchone()['total']
                
                return {
                    'system_active': True,
                    'total_rooms': room_count,
                    'total_zones': zone_count,
                    'active_schedules': schedule_count,
                    'total_plants': plant_count,
                    'water_usage_today': float(water_today),
                    'active_zones': [],  # Will be populated by active watering sessions
                    'last_watering': None,
                    'next_watering': None
                }
                
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                'system_active': False,
                'total_rooms': 0,
                'total_zones': 0,
                'active_schedules': 0,
                'total_plants': 0,
                'water_usage_today': 0,
                'active_zones': [],
                'last_watering': None,
                'next_watering': None
            }