# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-01-21

### Added
- Initial release of Smart Irrigation Controller
- Multi-room support for vegetative and flowering rooms
- Advanced zone management with configurable plant counts
- Flexible scheduling system (daily/weekly)
- Manual watering controls with adjustable duration
- Real-time web dashboard with WebSocket updates
- Home Assistant integration with switch control
- Custom dashboard cards for Home Assistant
- Water usage tracking and monitoring
- REST API for external integrations
- Support for 2L/hour drippers in 8L coco pots
- Automatic pump and solenoid control
- Responsive web interface with Bootstrap 5
- Docker-based addon architecture

### Features
- **Room Management**: Create and manage separate growing rooms
- **Zone Control**: Configure irrigation zones with pump/solenoid entities
- **Scheduling**: Set up automated watering schedules
- **Manual Control**: Instant manual watering with custom duration
- **Monitoring**: Real-time status updates and water usage tracking
- **Integration**: Seamless Home Assistant addon installation
- **Dashboard**: Custom Lovelace cards for system monitoring

### Technical Details
- Python 3 backend with Flask and SocketIO
- Bootstrap 5 responsive frontend
- SQLite-based configuration storage
- Docker containerization
- Home Assistant Supervisor integration
- RESTful API architecture

### Supported Hardware
- Raspberry Pi (all models)
- x86/x64 systems
- ARM-based systems
- GPIO-controlled pumps and solenoids
- 2L/hour precision drippers

### Documentation
- Complete installation guide
- Configuration examples
- API documentation
- Troubleshooting guide
- Hardware setup instructions