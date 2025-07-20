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
from irrigation_controller import IrrigationController
from ha_integration import HomeAssistantIntegration

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder='/www/templates', static_folder='/www/static')
app.config['SECRET_KEY'] = 'irrigation_secret_key'

# Configure for Home Assistant ingress
@app.after_request
def after_request(response):
    # Allow embedding in Home Assistant iframe
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"
    return response

socketio = SocketIO(app, cors_allowed_origins="*")

# Global controller instance
controller = None
ha_integration = None

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    """Get all configured rooms"""
    return jsonify(controller.get_rooms())

@app.route('/api/rooms', methods=['POST'])
def create_room():
    """Create a new room"""
    data = request.json
    result = controller.create_room(data)
    return jsonify(result)

@app.route('/api/rooms/<room_id>', methods=['PUT'])
def update_room(room_id):
    """Update room configuration"""
    data = request.json
    result = controller.update_room(room_id, data)
    return jsonify(result)

@app.route('/api/rooms/<room_id>', methods=['DELETE'])
def delete_room(room_id):
    """Delete a room"""
    result = controller.delete_room(room_id)
    return jsonify(result)

@app.route('/api/zones', methods=['GET'])
def get_zones():
    """Get all zones"""
    return jsonify(controller.get_zones())

@app.route('/api/zones', methods=['POST'])
def create_zone():
    """Create a new irrigation zone"""
    data = request.json
    result = controller.create_zone(data)
    return jsonify(result)

@app.route('/api/schedules', methods=['GET'])
def get_schedules():
    """Get all irrigation schedules"""
    return jsonify(controller.get_schedules())

@app.route('/api/schedules', methods=['POST'])
def create_schedule():
    """Create a new irrigation schedule"""
    data = request.json
    result = controller.create_schedule(data)
    return jsonify(result)

@app.route('/api/manual-water', methods=['POST'])
def manual_water():
    """Manually trigger watering for a zone"""
    data = request.json
    zone_id = data.get('zone_id')
    duration = data.get('duration', 60)  # Default 1 minute
    
    result = controller.manual_water(zone_id, duration)
    return jsonify(result)

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current system status"""
    return jsonify(controller.get_status())

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    emit('status_update', controller.get_status())

def schedule_runner():
    """Background thread to run scheduled tasks"""
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    parser = argparse.ArgumentParser(description='Smart Irrigation Controller')
    parser.add_argument('--port', type=int, default=8099, help='Web server port')
    parser.add_argument('--log-level', default='info', help='Log level')
    args = parser.parse_args()
    
    # Set log level
    log_level = getattr(logging, args.log_level.upper())
    logging.getLogger().setLevel(log_level)
    
    # Initialize controller
    global controller, ha_integration
    controller = IrrigationController()
    ha_integration = HomeAssistantIntegration()
    
    # Start schedule runner in background
    schedule_thread = threading.Thread(target=schedule_runner, daemon=True)
    schedule_thread.start()
    
    logger.info(f"Starting Smart Irrigation Controller on port {args.port}")
    socketio.run(app, host='0.0.0.0', port=args.port, debug=False, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    main()