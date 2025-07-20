# Changelog

All notable changes to this project will be documented in this file.

## [1.0.6] - 2025-01-21

### Fixed
- Fixed 503 Service Unavailable error with ingress
- Removed configurable port for ingress compatibility
- Fixed ingress port configuration for Home Assistant
- Added health check endpoint for debugging
- Simplified ingress setup for better reliability

### Changed
- Fixed port 8099 for ingress (no longer configurable)
- Updated run script to work with ingress
- Improved logging for ingress troubleshooting

## [1.0.5] - 2025-01-21

### Added
- Home Assistant ingress support for embedded UI
- UI now runs inside Home Assistant interface (no external window)
- Added proper iframe headers for Home Assistant integration
- Ingress port configuration for seamless integration

### Changed
- Removed external port exposure in favor of ingress
- Updated Flask app configuration for Home Assistant embedding
- UI accessible directly through Home Assistant sidebar

## [1.0.4] - 2025-01-21

### Fixed
- Fixed Flask-SocketIO production server error
- Added allow_unsafe_werkzeug=True parameter to enable server startup
- Resolved RuntimeError about Werkzeug web server in production

### Changed
- Updated SocketIO server configuration for Home Assistant addon environment

## [1.0.3] - 2025-01-21

### Fixed
- Fixed Python module import errors (yaml, flask, requests)
- Install all Python dependencies via pip in virtual environment for consistency
- Resolved ModuleNotFoundError for yaml and other system packages

### Changed
- Use pip for all Python packages instead of mixing system and pip packages
- Ensures all modules are available in the virtual environment

## [1.0.2] - 2025-01-21

### Fixed
- Fixed Docker build issues with Python environment management
- Updated Dockerfile to use virtual environment for Python packages
- Fixed ARG BUILD_FROM default value issue
- Simplified build process by removing unnecessary npm build steps
- Resolved Alpine Linux externally-managed-environment error

### Changed
- Use Python virtual environment instead of system-wide pip installation
- Streamlined Docker build process for better compatibility

## [1.0.1] - 2025-01-21

### Fixed
- Removed GitHub Actions workflow to allow Home Assistant local building
- Removed Docker image reference from config.yaml for local builds
- Cleaned up build configuration for Home Assistant Supervisor compatibility

### Changed
- Addon now builds locally in Home Assistant instead of pulling from registry
- Simplified deployment process for easier installation

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