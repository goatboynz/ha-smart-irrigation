// Smart Irrigation Controller JavaScript

// Initialize Socket.IO connection
const socket = io();

// Global variables
let rooms = [];
let zones = [];
let schedules = [];
let entities = [];

// Test JavaScript function
function testJavaScript() {
    console.log('testJavaScript called');
    alert('JavaScript is working! Check console for more details.');
    
    // Test API call
    fetch('/api/rooms')
        .then(response => response.json())
        .then(data => {
            console.log('API test result:', data);
            showAlert('API test successful - check console', 'success');
        })
        .catch(error => {
            console.error('API test error:', error);
            showAlert('API test failed - check console', 'danger');
        });
}

// Make functions globally available
window.saveRoom = saveRoom;
window.saveZone = saveZone;
window.saveSchedule = saveSchedule;
window.manualWater = manualWater;
window.testJavaScript = testJavaScript;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Smart Irrigation Controller JavaScript loaded');
    loadData();
    setupSocketListeners();
    setupEventListeners();
    
    // Test if saveRoom function is available
    if (typeof saveRoom === 'function') {
        console.log('saveRoom function is available');
    } else {
        console.error('saveRoom function is NOT available');
    }
    
    // Test API connectivity
    fetch('/api/rooms')
        .then(response => response.json())
        .then(data => {
            console.log('Initial API test successful:', data);
        })
        .catch(error => {
            console.error('Initial API test failed:', error);
        });
    
    // Add debug test function
    window.testAddRoomDirect = function() {
        console.log('Testing Add Room API directly');
        fetch('/api/rooms', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({name: 'Debug Test Room', type: 'vegetative', description: 'Test room from debug'})
        })
        .then(response => {
            console.log('API Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('API Response data:', data);
            alert('API Response: ' + JSON.stringify(data));
            if (data.success) {
                loadRooms(); // Reload rooms if successful
            }
        })
        .catch(error => {
            console.error('API Error:', error);
            alert('API Error: ' + error);
        });
    };
});

// Socket.IO event listeners
function setupSocketListeners() {
    socket.on('connect', function() {
        console.log('Connected to server');
    });

    socket.on('status_update', function(status) {
        updateStatusDisplay(status);
    });
}

// Setup event listeners
function setupEventListeners() {
    // Tab change events
    document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(event) {
            const target = event.target.getAttribute('data-bs-target');
            if (target === '#rooms') {
                loadRooms();
            } else if (target === '#zones') {
                loadZones();
            } else if (target === '#schedules') {
                loadSchedules();
            }
        });
    });
}

// Load initial data
async function loadData() {
    try {
        await Promise.all([
            loadRooms(),
            loadZones(),
            loadSchedules(),
            loadStatus(),
            loadEntities()
        ]);
        updateManualControlOptions();
    } catch (error) {
        console.error('Error loading data:', error);
        showAlert('Error loading data', 'danger');
    }
}

// Load rooms
async function loadRooms() {
    try {
        const response = await fetch('/api/rooms');
        rooms = await response.json();
        displayRooms();
        updateRoomSelects();
        updateStatusCards();
    } catch (error) {
        console.error('Error loading rooms:', error);
    }
}

// Load zones
async function loadZones() {
    try {
        const response = await fetch('/api/zones');
        zones = await response.json();
        displayZones();
        updateZoneSelects();
        updateStatusCards();
    } catch (error) {
        console.error('Error loading zones:', error);
    }
}

// Load schedules
async function loadSchedules() {
    try {
        const response = await fetch('/api/schedules');
        schedules = await response.json();
        displaySchedules();
    } catch (error) {
        console.error('Error loading schedules:', error);
    }
}

// Load system status
async function loadStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();
        updateStatusDisplay(status);
        
        // Also load detailed stats
        await loadDetailedStats();
    } catch (error) {
        console.error('Error loading status:', error);
    }
}

// Load detailed statistics
async function loadDetailedStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();
        updateDetailedStatsDisplay(stats);
    } catch (error) {
        console.error('Error loading detailed stats:', error);
    }
}

// Load Home Assistant entities
async function loadEntities() {
    try {
        const response = await fetch('/api/entities');
        const data = await response.json();
        entities = data.switches || [];
        updateEntitySelects();
    } catch (error) {
        console.error('Error loading entities:', error);
        entities = [];
    }
}

// Display rooms
function displayRooms() {
    const container = document.getElementById('rooms-list');
    if (rooms.length === 0) {
        container.innerHTML = '<div class="col-12"><p class="text-muted">No rooms configured yet.</p></div>';
        return;
    }

    container.innerHTML = rooms.map(room => `
        <div class="col-md-6 mb-3">
            <div class="card">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h6 class="mb-0">
                        <i class="fas fa-${room.type === 'vegetative' ? 'leaf' : 'flower'} me-2"></i>
                        ${room.name}
                    </h6>
                    <span class="badge bg-${room.type === 'vegetative' ? 'success' : 'warning'}">${room.type}</span>
                </div>
                <div class="card-body">
                    <p class="card-text">${room.description || 'No description'}</p>
                    <small class="text-muted">Zones: ${room.zones ? room.zones.length : 0}</small>
                </div>
                <div class="card-footer">
                    <button class="btn btn-sm btn-outline-primary" onclick="editRoom('${room.id}')">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteRoom('${room.id}')">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// Display zones
function displayZones() {
    const container = document.getElementById('zones-list');
    if (zones.length === 0) {
        container.innerHTML = '<p class="text-muted">No zones configured yet.</p>';
        return;
    }

    container.innerHTML = zones.map(zone => {
        const room = rooms.find(r => r.id === zone.room_id);
        return `
            <div class="card mb-3">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h6 class="mb-0">
                        <i class="fas fa-map-marker-alt me-2"></i>
                        ${zone.name}
                    </h6>
                    <span class="badge bg-${zone.active ? 'success' : 'secondary'}">
                        ${zone.active ? 'Active' : 'Inactive'}
                    </span>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>Room:</strong> ${room ? room.name : 'Unknown'}</p>
                            <p><strong>Plants:</strong> ${zone.plant_count}</p>
                            <p><strong>Flow Rate:</strong> ${zone.flow_rate}L/h</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Pump:</strong> ${zone.pump_entity || 'Not configured'}</p>
                            <p><strong>Solenoid:</strong> ${zone.solenoid_entity || 'Not configured'}</p>
                        </div>
                    </div>
                </div>
                <div class="card-footer">
                    <button class="btn btn-sm btn-primary" onclick="manualWaterZone('${zone.id}')">
                        <i class="fas fa-tint"></i> Water Now
                    </button>
                    <button class="btn btn-sm btn-outline-primary" onclick="editZone('${zone.id}')">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteZone('${zone.id}')">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

// Display schedules
function displaySchedules() {
    const container = document.getElementById('schedules-list');
    if (schedules.length === 0) {
        container.innerHTML = '<p class="text-muted">No schedules configured yet.</p>';
        return;
    }

    container.innerHTML = schedules.map(schedule => {
        const zone = zones.find(z => z.id === schedule.zone_id);
        return `
            <div class="card mb-3">
                <div class="card-header d-flex justify-content-between align-items-center">
                    <h6 class="mb-0">
                        <i class="fas fa-clock me-2"></i>
                        ${schedule.name}
                    </h6>
                    <span class="badge bg-${schedule.active ? 'success' : 'secondary'}">
                        ${schedule.active ? 'Active' : 'Inactive'}
                    </span>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <p><strong>Zone:</strong> ${zone ? zone.name : 'Unknown'}</p>
                            <p><strong>Duration:</strong> ${schedule.duration} minutes</p>
                        </div>
                        <div class="col-md-6">
                            <p><strong>Frequency:</strong> ${schedule.frequency}</p>
                            <p><strong>Times:</strong> ${schedule.times.join(', ')}</p>
                        </div>
                    </div>
                </div>
                <div class="card-footer">
                    <button class="btn btn-sm btn-outline-primary" onclick="editSchedule('${schedule.id}')">
                        <i class="fas fa-edit"></i> Edit
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteSchedule('${schedule.id}')">
                        <i class="fas fa-trash"></i> Delete
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

// Update status display
function updateStatusDisplay(status) {
    document.getElementById('active-zones-count').textContent = status.active_zones.length;
    document.getElementById('water-usage').textContent = status.water_usage_today.toFixed(1) + 'L';
    
    // Update system status indicator
    const statusElement = document.getElementById('system-status');
    if (status.system_active) {
        statusElement.innerHTML = '<i class="fas fa-circle text-success me-1"></i>System Active';
    } else {
        statusElement.innerHTML = '<i class="fas fa-circle text-danger me-1"></i>System Inactive';
    }
}

// Update status cards
function updateStatusCards() {
    document.getElementById('total-rooms').textContent = rooms.length;
    document.getElementById('total-zones').textContent = zones.length;
}

// Update detailed stats display
function updateDetailedStatsDisplay(stats) {
    const container = document.getElementById('detailed-stats');
    
    if (!stats.rooms || stats.rooms.length === 0) {
        container.innerHTML = '<p class="text-muted">No statistics available yet</p>';
        return;
    }
    
    container.innerHTML = `
        <div class="row mb-3">
            <div class="col-12">
                <h6 class="text-primary">Total Water Used Today: ${stats.total_water_today.toFixed(2)}L</h6>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <h6><i class="fas fa-home me-1"></i>By Room</h6>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Room</th>
                                <th>Type</th>
                                <th>Plants</th>
                                <th>Water Used</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${stats.rooms.map(room => `
                                <tr>
                                    <td><strong>${room.name}</strong></td>
                                    <td><span class="badge bg-${room.type === 'vegetative' ? 'success' : 'warning'}">${room.type}</span></td>
                                    <td>${room.plants_count}</td>
                                    <td>${room.water_used_today}L</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div class="col-md-6">
                <h6><i class="fas fa-map-marker-alt me-1"></i>By Zone</h6>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Zone</th>
                                <th>Room</th>
                                <th>Plants</th>
                                <th>Water Used</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${stats.zones.map(zone => `
                                <tr class="${zone.active ? '' : 'text-muted'}">
                                    <td><strong>${zone.name}</strong></td>
                                    <td>${zone.room_name}</td>
                                    <td>${zone.plant_count}</td>
                                    <td>${zone.water_used_today}L</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
}

// Update room select options
function updateRoomSelects() {
    const selects = document.querySelectorAll('#zoneRoom');
    selects.forEach(select => {
        select.innerHTML = '<option value="">Select room...</option>' +
            rooms.map(room => `<option value="${room.id}">${room.name}</option>`).join('');
    });
}

// Update zone select options
function updateZoneSelects() {
    const selects = document.querySelectorAll('#scheduleZone, #manual-zone');
    selects.forEach(select => {
        select.innerHTML = '<option value="">Choose zone...</option>' +
            zones.map(zone => `<option value="${zone.id}">${zone.name}</option>`).join('');
    });
}

// Update entity select options
function updateEntitySelects() {
    const selects = document.querySelectorAll('#pumpEntity, #solenoidEntity');
    selects.forEach(select => {
        const currentValue = select.value;
        select.innerHTML = '<option value="">Select entity...</option>' +
            entities.map(entity => `<option value="${entity.id}">${entity.name}</option>`).join('');
        if (currentValue) {
            select.value = currentValue;
        }
    });
}

// Update manual control options
function updateManualControlOptions() {
    updateZoneSelects();
}

// Save room
async function saveRoom() {
    console.log('saveRoom function called');
    
    const name = document.getElementById('roomName').value;
    const type = document.getElementById('roomType').value;
    const description = document.getElementById('roomDescription').value;

    console.log('Form values:', { name, type, description });

    if (!name) {
        showAlert('Please enter a room name', 'warning');
        return;
    }

    try {
        console.log('Sending request to /api/rooms');
        const response = await fetch('/api/rooms', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                type: type,
                description: description
            })
        });

        console.log('Response status:', response.status);
        const result = await response.json();
        console.log('Response result:', result);
        
        if (result.success) {
            showAlert('Room created successfully', 'success');
            document.getElementById('roomForm').reset();
            bootstrap.Modal.getInstance(document.getElementById('roomModal')).hide();
            loadRooms();
        } else {
            showAlert('Error creating room: ' + result.error, 'danger');
        }
    } catch (error) {
        console.error('Error saving room:', error);
        showAlert('Error saving room', 'danger');
    }
}

// Save zone
async function saveZone() {
    const name = document.getElementById('zoneName').value;
    const roomId = document.getElementById('zoneRoom').value;
    const plantCount = parseInt(document.getElementById('plantCount').value);
    const pumpEntity = document.getElementById('pumpEntity').value;
    const solenoidEntity = document.getElementById('solenoidEntity').value;

    if (!name || !roomId) {
        showAlert('Please fill in all required fields', 'warning');
        return;
    }

    try {
        const response = await fetch('/api/zones', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                room_id: roomId,
                plant_count: plantCount,
                pump_entity: pumpEntity,
                solenoid_entity: solenoidEntity
            })
        });

        const result = await response.json();
        if (result.success) {
            showAlert('Zone created successfully', 'success');
            document.getElementById('zoneForm').reset();
            bootstrap.Modal.getInstance(document.getElementById('zoneModal')).hide();
            loadZones();
        } else {
            showAlert('Error creating zone: ' + result.error, 'danger');
        }
    } catch (error) {
        console.error('Error saving zone:', error);
        showAlert('Error saving zone', 'danger');
    }
}

// Save schedule
async function saveSchedule() {
    const name = document.getElementById('scheduleName').value;
    const zoneId = document.getElementById('scheduleZone').value;
    const duration = parseInt(document.getElementById('scheduleDuration').value);
    const frequency = document.getElementById('scheduleFrequency').value;
    const timesText = document.getElementById('scheduleTimes').value;

    if (!name || !zoneId || !timesText) {
        showAlert('Please fill in all required fields', 'warning');
        return;
    }

    const times = timesText.split('\n').map(t => t.trim()).filter(t => t);

    try {
        const response = await fetch('/api/schedules', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                zone_id: zoneId,
                duration: duration,
                frequency: frequency,
                times: times
            })
        });

        const result = await response.json();
        if (result.success) {
            showAlert('Schedule created successfully', 'success');
            document.getElementById('scheduleForm').reset();
            bootstrap.Modal.getInstance(document.getElementById('scheduleModal')).hide();
            loadSchedules();
        } else {
            showAlert('Error creating schedule: ' + result.error, 'danger');
        }
    } catch (error) {
        console.error('Error saving schedule:', error);
        showAlert('Error saving schedule', 'danger');
    }
}

// Manual watering
async function manualWater() {
    const zoneId = document.getElementById('manual-zone').value;
    const duration = parseInt(document.getElementById('manual-duration').value);

    if (!zoneId) {
        showAlert('Please select a zone', 'warning');
        return;
    }

    try {
        const response = await fetch('/api/manual-water', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                zone_id: zoneId,
                duration: duration
            })
        });

        const result = await response.json();
        if (result.success) {
            showAlert(result.message, 'success');
        } else {
            showAlert('Error starting watering: ' + result.error, 'danger');
        }
    } catch (error) {
        console.error('Error starting manual watering:', error);
        showAlert('Error starting watering', 'danger');
    }
}

// Manual water zone (from zone card)
function manualWaterZone(zoneId) {
    document.getElementById('manual-zone').value = zoneId;
    document.getElementById('manual-duration').value = 2;
    
    // Switch to dashboard tab
    const dashboardTab = new bootstrap.Tab(document.getElementById('dashboard-tab'));
    dashboardTab.show();
    
    // Trigger manual watering
    setTimeout(() => manualWater(), 100);
}

// Show alert
function showAlert(message, type) {
    const alertContainer = document.createElement('div');
    alertContainer.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertContainer.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertContainer.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertContainer);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertContainer.parentNode) {
            alertContainer.remove();
        }
    }, 5000);
}

// Placeholder functions for edit/delete operations
function editRoom(roomId) {
    showAlert('Edit room functionality coming soon', 'info');
}

function deleteRoom(roomId) {
    if (confirm('Are you sure you want to delete this room?')) {
        showAlert('Delete room functionality coming soon', 'info');
    }
}

function editZone(zoneId) {
    showAlert('Edit zone functionality coming soon', 'info');
}

function deleteZone(zoneId) {
    if (confirm('Are you sure you want to delete this zone?')) {
        showAlert('Delete zone functionality coming soon', 'info');
    }
}

function editSchedule(scheduleId) {
    showAlert('Edit schedule functionality coming soon', 'info');
}

function deleteSchedule(scheduleId) {
    if (confirm('Are you sure you want to delete this schedule?')) {
        showAlert('Delete schedule functionality coming soon', 'info');
    }
}