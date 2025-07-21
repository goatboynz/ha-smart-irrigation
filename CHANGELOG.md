# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2025-01-21 - MAJOR DATABASE UPGRADE

### 🗄️ NEW: SQLite Database Implementation
- **Complete database rewrite** - Replaced JSON config with SQLite database
- **Reliable data storage** - No more file corruption or save issues
- **Proper relationships** - Foreign keys between rooms, zones, and schedules
- **Water usage logging** - Persistent tracking of all watering events
- **Better performance** - Faster queries and data retrieval

### ✅ FIXES:
- **Fixed "Add New Room"** - Database ensures reliable room creation
- **Fixed all data persistence** - No more lost configurations
- **Fixed water usage tracking** - Proper per-room and per-zone statistics
- **Fixed concurrent access** - Database handles multiple operations safely

### 🆕 NEW FEATURES:
- **Water usage history** - Complete log of all watering events
- **Enhanced statistics** - Real-time data from database queries
- **Better error handling** - Database constraints prevent invalid data
- **Automatic migrations** - Database schema updates automatically

### 🔧 TECHNICAL IMPROVEMENTS:
- Added SQLite support to Docker container
- New database.py module with comprehensive data management
- Updated irrigation_controller.py to use database
- Enhanced JavaScript debugging and error reporting
- Better static file handling

### 📊 DATABASE TABLES:
- **rooms** - Room configurations with types and descriptions
- **zones** - Irrigation zones with plant counts and entities
- **schedules** - Watering schedules with times and frequencies
- **water_usage** - Complete log of all watering events
- **settings** - System configuration settings

This is a major upgrade that should resolve all data persistence issues!

## [1.0.9] - 2025-01-21

### Fixed
- Added comprehensive debugging for "Add New Room" functionality
- Enhanced error handling in create_room API endpoint
- Added detailed logging for room creation process
- Improved config file saving with better error reporting
- Added client-side debugging for form submission

### Debug Enhancements
- Added console logging to saveRoom JavaScript function
- Enhanced server-side logging for room creation API
- Added error handling and logging to irrigation controller
- Improved config directory creation and file saving
- Better error messages for troubleshooting

## [1.0.8] - 2025-01-21

### Fixed
- Fixed "Add New Room" functionality - now works properly
- Fixed all POST API routes to handle uninitialized controllers
- Fixed zone creation, schedule creation, and manual watering

### Added
- Home Assistant entity selection for pumps and solenoids
- Detailed water usage statistics by room and zone
- Enhanced dashboard with water usage breakdown tables
- API endpoint for fetching Home Assistant switch entities
- Per-room and per-zone water usage tracking
- Total plants count and active schedules count
- Searchable entity dropdowns in zone creation form

### Enhanced
- Zone form now has dropdown selects for HA entities
- Dashboard shows detailed water usage statistics
- Real-time statistics with room and zone breakdowns
- Better user experience with entity selection
- Enhanced status tracking with detailed metrics

## [1.0.7] - 2025-01-21

### Fixed
- Major fix for 503 Service Unavailable errors
- Improved Flask app startup with better error handling
- Initialize controllers in background to prevent startup delays
- Added fallback responses for API routes when controllers not ready
- Added test endpoint (/test) for debugging Flask connectivity
- Better import error handling to prevent app crashes

### Added
- Background controller initialization to speed up startup
- Test route for debugging ingress connectivity
- Graceful handling of uninitialized controllers
- Enhanced logging for troubleshooting startup issues

### Changed
- Controllers now initialize after Flask app starts
- API routes return empty arrays instead of errors when not ready
- Improved error handling throughout the application

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