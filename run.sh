#!/usr/bin/with-contenv bashio

# Get configuration
LOG_LEVEL=$(bashio::config 'log_level')

bashio::log.info "Starting Smart Irrigation Controller..."
bashio::log.info "Log level: ${LOG_LEVEL}"
bashio::log.info "Using ingress on port 8099"

# Start the irrigation controller
cd /app
python3 main.py --log-level="${LOG_LEVEL}"