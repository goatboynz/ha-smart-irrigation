# Smart Irrigation Controller - Home Assistant Addon

A comprehensive irrigation control system designed for hydroponic and soil-based growing operations. Perfect for managing vegetative and flowering rooms with precise watering schedules and real-time monitoring.

## Features

### 🌱 **Multi-Room Support**
- Configure separate vegetative and flowering rooms
- Independent zone management per room
- Room-specific settings and monitoring

### 💧 **Advanced Zone Control**
- Support for multiple irrigation zones per room
- Integration with Home Assistant switches for pumps and solenoids
- Configurable plant counts and flow rates
- 2L/hour drippers with dual-dripper setup per plant

### ⏰ **Flexible Scheduling**
- Daily and weekly watering schedules
- Multiple watering times per day
- Custom duration settings
- Schedule activation/deactivation

### 🎛️ **Manual Control**
- Instant manual watering triggers
- Adjustable duration controls
- Emergency stop functionality
- Real-time status monitoring

### 📊 **Dashboard & Monitoring**
- Beautiful web interface
- Real-time status updates via WebSocket
- Water usage tracking
- Active watering session monitoring

### 🏠 **Home Assistant Integration**
- Custom dashboard cards
- Sensor data publishing
- Switch entity integration
- Seamless addon installation

## Installation

### Method 1: GitHub Repository (Recommended)

1. **Add Repository to Home Assistant:**
   - Go to **Supervisor** → **Add-on Store**
   - Click the **⋮** menu → **Repositories**
   - Add: `https://github.com/goatboynz/ha-smart-irrigation`
   - Click **Add**

2. **Install the Addon:**
   - Find "Smart Irrigation Controller" in the add-on store
   - Click **Install**
   - Wait for installation to complete

3. **Configure the Addon:**
   - Go to **Configuration** tab
   - Set your preferred web port (default: 8099)
   - Set log level (info recommended)
   - Click **Save**

4. **Start the Addon:**
   - Go to **Info** tab
   - Click **Start**
   - Enable **Auto-start** and **Watchdog**

### Method 2: Local Installation

1. Copy this entire folder to `/addons/smart_irrigation/` in your Home Assistant config
2. Restart Home Assistant
3. Install from the local add-ons section

## Configuration

### Basic Setup

```yaml
log_level: info
web_port: 8099
```

### Home Assistant Integration

The addon automatically integrates with Home Assistant. Ensure your pump and solenoid switches are properly configured:

```yaml
# Example switch configuration in configuration.yaml
switch:
  - platform: gpio
    pins:
      18: Pump Zone 1
      19: Solenoid Zone 1
      20: Pump Zone 2
      21: Solenoid Zone 2
```

## Usage

### 1. Access the Web Interface
- Open `http://homeassistant.local:8099` in your browser
- Or use the **Open Web UI** button in the addon info

### 2. Configure Rooms
- Go to the **Rooms** tab
- Click **Add Room**
- Configure:
  - Room name (e.g., "Veg Room", "Flower Room")
  - Room type (Vegetative/Flowering)
  - Description

### 3. Setup Irrigation Zones
- Go to the **Zones** tab
- Click **Add Zone**
- Configure:
  - Zone name
  - Associated room
  - Number of plants
  - Home Assistant switch entities for pump and solenoid

### 4. Create Watering Schedules
- Go to the **Schedules** tab
- Click **Add Schedule**
- Configure:
  - Schedule name
  - Target zone
  - Watering duration
  - Frequency (daily/weekly)
  - Watering times

### 5. Manual Control
- Use the **Dashboard** tab for manual watering
- Select zone and duration
- Click **Start Watering**

## Home Assistant Dashboard Cards

### Installation
1. Copy `custom_cards/irrigation-status-card.js` to `/config/www/`
2. Add to your Lovelace resources:

```yaml
resources:
  - url: /local/irrigation-status-card.js
    type: module
```

### Usage
Add to your dashboard:

```yaml
type: custom:irrigation-status-card
title: "Irrigation System"
addon_url: "http://homeassistant.local:8099"
```

## Growing Medium Specifications

This system is optimized for:
- **Container Size:** 8L pots
- **Growing Medium:** Coco coir
- **Dripper Setup:** 2 × 2L/hour drippers per plant
- **Flow Rate:** 4L/hour per plant (adjustable)

## API Endpoints

The addon provides a REST API for advanced integrations:

- `GET /api/status` - System status
- `GET /api/rooms` - List all rooms
- `POST /api/rooms` - Create new room
- `GET /api/zones` - List all zones
- `POST /api/zones` - Create new zone
- `GET /api/schedules` - List all schedules
- `POST /api/schedules` - Create new schedule
- `POST /api/manual-water` - Trigger manual watering

## Troubleshooting

### Common Issues

**Addon won't start:**
- Check logs in the addon **Log** tab
- Verify port 8099 is not in use
- Ensure Home Assistant has sufficient resources

**Switches not working:**
- Verify switch entity IDs are correct
- Check Home Assistant switch states
- Ensure proper GPIO/hardware configuration

**Web interface not accessible:**
- Check if addon is running
- Verify port configuration
- Check firewall settings

### Logs
Access detailed logs via:
- Addon **Log** tab in Home Assistant
- Web interface system status
- Home Assistant system logs

## Support

For issues and feature requests:
1. Check the [GitHub Issues](https://github.com/goatboynz/ha-smart-irrigation/issues)
2. Create a new issue with:
   - Addon version
   - Home Assistant version
   - Detailed problem description
   - Relevant log entries

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Happy Growing! 🌱**