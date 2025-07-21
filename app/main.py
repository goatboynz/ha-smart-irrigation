#!/usr/bin/env python3
"""
Smart Irrigation Controller for Home Assistant
Main application entry point
"""

import os
import sys
import json
import yaml
import logging
import argparse
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import requests
import schedule
import time
import threading

# Setup logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder='/www/templates', static_folder='/www/static')
app.config['SECRET_KEY'] = 'irrigation_secret_key'

# Add logging for static file requests
@app.before_request
def log_request_info():
    if request.path.startswith('/static/'):
        logger.info(f"Static file request: {request.path}")
    elif request.path.startswith('/api/'):
        logger.info(f"API request: {request.method} {request.path}")

# Configure for Home Assistant ingress
@app.after_request
def after_request(response):
    # Allow embedding in Home Assistant iframe
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
    return response

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Global controller instance (initialize later to avoid startup delays)
controller = None
ha_integration = None

# Import modules after Flask setup to catch any import errors
try:
    from irrigation_controller import IrrigationController
    from ha_integration import HomeAssistantIntegration
    logger.info("Successfully imported irrigation modules")
except Exception as e:
    logger.error(f"Error importing modules: {e}")
    # Continue anyway to get basic web interface running

@app.route('/')
def index():
    """Main dashboard page"""
    logger.info("Index route accessed")
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index template: {e}")
        return f"<h1>Smart Irrigation Controller</h1><p>Template error: {e}</p><p><a href='/health'>Health Check</a></p><p><a href='/test-js'>Test JavaScript</a></p>"

@app.route('/health')
def health():
    """Health check endpoint"""
    logger.info("Health check accessed")
    return {'status': 'ok', 'service': 'Smart Irrigation Controller', 'timestamp': datetime.now().isoformat()}

@app.route('/debug')
def debug_menu():
    """Debug menu for troubleshooting"""
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Debug Menu</title></head>
    <body>
        <h1>Smart Irrigation Debug Menu</h1>
        <ul>
            <li><a href="/debug/create-test-room">Create Test Room</a></li>
            <li><a href="/debug/list-rooms">List All Rooms</a></li>
            <li><a href="/health">Health Check</a></li>
            <li><a href="/">Back to Main App</a></li>
        </ul>
    </body>
    </html>
    '''

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    """Get all configured rooms"""
    if controller is None:
        return jsonify({'error': 'Controller not initialized yet', 'rooms': []})
    return jsonify(controller.get_rooms())

@app.route('/api/rooms', methods=['POST'])
def create_room():
    """Create a new room"""
    logger.info("Create room API called")
    if controller is None:
        logger.error("Controller not initialized")
        return jsonify({'success': False, 'error': 'Controller not initialized yet'})
    
    data = request.json
    logger.info(f"Room data received: {data}")
    
    try:
        result = controller.create_room(data)
        logger.info(f"Room creation result: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error creating room: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/zones', methods=['GET'])
def get_zones():
    """Get all zones"""
    if controller is None:
        return jsonify([])
    return jsonify(controller.get_zones())

@app.route('/api/zones', methods=['POST'])
def create_zone():
    """Create a new irrigation zone"""
    if controller is None:
        return jsonify({'success': False, 'error': 'Controller not initialized yet'})
    data = request.json
    result = controller.create_zone(data)
    return jsonify(result)

@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    """Get all irrigation schedules"""
    if controller is None:
        return jsonify([])
    return jsonify(controller.get_schedules())

@app.route('/api/schedules', methods=['POST'])
def create_schedule():
    """Create a new irrigation schedule"""
    if controller is None:
        return jsonify({'success': False, 'error': 'Controller not initialized yet'})
    data = request.json
    result = controller.create_schedule(data)
    return jsonify(result)

@app.route('/api/manual-water', methods=['POST'])
def manual_water():
    """Manually trigger watering for a zone"""
    if controller is None:
        return jsonify({'success': False, 'error': 'Controller not initialized yet'})
    data = request.json
    zone_id = data.get('zone_id')
    duration = data.get('duration', 60)  # Default 1 minute
    
    result = controller.manual_water(zone_id, duration)
    return jsonify(result)

@app.route('/api/entities', methods=['GET'])
def get_entities():
    """Get Home Assistant switch entities"""
    if ha_integration is None:
        return jsonify({'switches': [], 'error': 'Home Assistant integration not initialized'})
    
    try:
        switches = ha_integration.get_all_switches()
        # Format for dropdown
        entities = [{'id': switch['entity_id'], 'name': switch['attributes'].get('friendly_name', switch['entity_id'])} 
                   for switch in switches]
        return jsonify({'switches': entities})
    except Exception as e:
        logger.error(f"Error getting entities: {e}")
        return jsonify({'switches': [], 'error': str(e)})

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current system status"""
    if controller is None:
        return jsonify({'system_active': False, 'active_zones': [], 'water_usage_today': 0, 'status': 'initializing'})
    return jsonify(controller.get_status())

@app.route('/api/stats', methods=['GET'])
def get_detailed_stats():
    """Get detailed statistics with room and zone breakdowns"""
    if controller is None:
        return jsonify({'total_water_today': 0, 'rooms': [], 'zones': []})
    return jsonify(controller.get_detailed_stats())

@app.route('/debug/create-test-room')
def debug_create_test_room():
    """Debug endpoint to test room creation"""
    logger.info("Debug create test room called")
    if controller is None:
        return jsonify({'success': False, 'error': 'Controller not initialized'})
    
    test_data = {
        'name': f'Test Room {datetime.now().strftime("%H:%M:%S")}',
        'type': 'vegetative',
        'description': 'Debug test room created via direct endpoint'
    }
    
    try:
        result = controller.create_room(test_data)
        logger.info(f"Debug room creation result: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Debug room creation error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/debug/list-rooms')
def debug_list_rooms():
    """Debug endpoint to list all rooms"""
    logger.info("Debug list rooms called")
    if controller is None:
        return jsonify({'rooms': [], 'error': 'Controller not initialized'})
    
    try:
        rooms = controller.get_rooms()
        logger.info(f"Debug rooms list: {rooms}")
        return jsonify({'rooms': rooms, 'count': len(rooms)})
    except Exception as e:
        logger.error(f"Debug list rooms error: {e}")
        return jsonify({'rooms': [], 'error': str(e)})

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    emit('status_update', controller.get_status() if controller else {})

def schedule_runner():
    """Background thread to run scheduled tasks"""
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    parser = argparse.ArgumentParser(description='Smart Irrigation Controller')
    parser.add_argument('--log-level', default='info', help='Log level')
    args = parser.parse_args()
    
    # For Home Assistant ingress, always use port 8099
    port = 8099
    
    # Set log level
    log_level = getattr(logging, args.log_level.upper())
    logging.getLogger().setLevel(log_level)
    
    # Initialize controllers in a separate thread to avoid blocking startup
    def initialize_controllers():
        global controller, ha_integration
        try:
            logger.info("Initializing irrigation controller...")
            controller = IrrigationController()
            logger.info("Initializing Home Assistant integration...")
            ha_integration = HomeAssistantIntegration()
            logger.info("Controllers initialized successfully")
            
            # Start schedule runner
            schedule_thread = threading.Thread(target=schedule_runner, daemon=True)
            schedule_thread.start()
            logger.info("Schedule runner started")
        except Exception as e:
            logger.error(f"Error initializing controllers: {e}")
    
    # Start controller initialization in background
    init_thread = threading.Thread(target=initialize_controllers, daemon=True)
    init_thread.start()
    
    logger.info(f"Starting Smart Irrigation Controller on port {port}")
    logger.info("Flask app starting - this should resolve 503 errors")
    
    try:
        # For Home Assistant ingress, bind to all interfaces
        socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True, use_reloader=False)
    except Exception as e:
        logger.error(f"Error starting Flask app: {e}")
        raise

if __name__ == '__main__':
    main()