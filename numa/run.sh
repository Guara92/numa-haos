#!/usr/bin/with-contenv bashio
# shellcheck shell=bash
# ==============================================================================
# Home Assistant App: Numa
# Legacy entrypoint — kept for reference.
# The active service definition is in:
#   rootfs/etc/s6-overlay/s6-rc.d/numa/run
# ==============================================================================

declare numa_config
declare log_level

# ------------------------------------------------------------------------------
# Read options
# ------------------------------------------------------------------------------
log_level=$(bashio::config 'log_level' 'info')
bashio::log.level "${log_level}"

# Wire RUST_LOG so Numa's env_logger picks up the selected verbosity.
export RUST_LOG="${log_level}"

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
#
# Numa CLI synopsis:  numa [command] [config-path]
# The config path is a positional argument — there is no --config flag.
# ------------------------------------------------------------------------------
bashio::log.info "Starting Numa DNS server..."
bashio::log.info "Using config: ${numa_config}"

exec /usr/local/bin/numa "${numa_config}"
