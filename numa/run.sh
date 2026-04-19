#!/usr/bin/with-contenv bashio
# ==============================================================================
# Home Assistant App: Numa
# Runs Numa DNS server
# ==============================================================================

declare numa_config
declare log_level

# ------------------------------------------------------------------------------
# Read options
# ------------------------------------------------------------------------------
log_level=$(bashio::config 'log_level' 'info')
bashio::log.level "${log_level}"

# ------------------------------------------------------------------------------
# Config file setup
# ------------------------------------------------------------------------------
numa_config="/config/numa.toml"

if ! bashio::fs.file_exists "${numa_config}"; then
    bashio::log.info "No numa.toml found, copying default config..."
    cp /etc/numa/numa.toml.default "${numa_config}"
fi

# ------------------------------------------------------------------------------
# Start Numa
# ------------------------------------------------------------------------------
bashio::log.info "Starting Numa DNS server..."
bashio::log.info "Using config: ${numa_config}"

exec /usr/local/bin/numa --config "${numa_config}"
