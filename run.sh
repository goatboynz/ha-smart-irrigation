#!/usr/bin/with-contenv bashio

# Get configuration
LOG_LEVEL=$(bashio::config 'log_level')
WEB_PORT=$(bashio::config 'web_port')

bashio::log.info "Starting Smart Irrigation Controller..."
bashio::log.info "Log level: ${LOG_LEVEL}"
bashio::log.info "Web port: ${WEB_PORT}"

# Start the irrigation controller
cd /app
python3 main.py --port="${WEB_PORT}" --log-level="${LOG_LEVEL}"