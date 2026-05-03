# NOTE: As of v0.13.1, Numa publishes official multi-arch Docker images at:
#   ghcr.io/razvandimescu/numa:latest  (amd64 + arm64)
# We intentionally do NOT use those as our base because the HA Supervisor
# requires the ghcr.io/hassio-addons/base image (which bundles s6-overlay,
# bashio, and all Supervisor integration hooks). Instead we download the
# pre-built binary from the GitHub release assets and install it on top.
ARG BUILD_FROM=ghcr.io/hassio-addons/base:20.0.4
# hadolint ignore=DL3006
FROM ${BUILD_FROM}

ARG BUILD_ARCH=amd64

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install runtime dependencies
# hadolint ignore=DL3018
RUN apk add --no-cache \
    curl \
    ca-certificates \
    nginx

# Download and install the Numa binary for the target architecture.
#
# Release asset naming:
#   aarch64 -> numa-linux-aarch64.tar.gz
#   amd64   -> numa-linux-x86_64.tar.gz
#
# Each archive is a flat tarball containing a single "numa" binary.
ARG NUMA_VERSION="v0.15.1"
# hadolint ignore=SC2155
RUN \
    if [[ "${BUILD_ARCH}" = "aarch64" ]]; then ARCH="aarch64"; \
    elif [[ "${BUILD_ARCH}" = "amd64" ]]; then ARCH="x86_64"; \
    else echo "Unsupported arch: ${BUILD_ARCH}" && exit 1; \
    fi \
    \
    && echo "Installing Numa ${NUMA_VERSION} for linux-${ARCH}..." \
    \
    && curl -fsSL \
    "https://github.com/razvandimescu/numa/releases/download/${NUMA_VERSION}/numa-linux-${ARCH}.tar.gz" \
    -o "/tmp/numa-linux-${ARCH}.tar.gz" \
    \
    && curl -fsSL \
    "https://github.com/razvandimescu/numa/releases/download/${NUMA_VERSION}/numa-linux-${ARCH}.tar.gz.sha256" \
    -o "/tmp/numa-linux-${ARCH}.tar.gz.sha256" \
    \
    && echo "$(awk '{print $1}' "/tmp/numa-linux-${ARCH}.tar.gz.sha256")  /tmp/numa-linux-${ARCH}.tar.gz" | sha256sum -c - \
    \
    && tar -xzf "/tmp/numa-linux-${ARCH}.tar.gz" -C /tmp/ \
    \
    && mv /tmp/numa /usr/local/bin/numa \
    \
    && chmod a+x /usr/local/bin/numa \
    \
    && numa --version \
    \
    && rm -rf /tmp/*

# Copy root filesystem (s6 service definitions, default config, etc.)
COPY rootfs /

RUN chmod a+x \
    /etc/s6-overlay/scripts/init-numa \
    /etc/s6-overlay/s6-rc.d/numa/run \
    /etc/s6-overlay/scripts/init-nginx \
    /etc/s6-overlay/s6-rc.d/nginx/run \
    /etc/s6-overlay/s6-rc.d/nginx/finish

# Health check — GET /health is a documented endpoint (src/health.rs + src/api.rs).
# Response shape: {"status":"ok","version":"...","uptime_secs":N,...}
# The check is intentionally lightweight: it only queries the loopback address.
HEALTHCHECK \
    --interval=30s \
    --timeout=10s \
    --start-period=20s \
    CMD curl --fail http://127.0.0.1:5381/health || exit 1

# Build arguments (injected by the HA build system / CI)
ARG BUILD_DATE
ARG BUILD_DESCRIPTION
ARG BUILD_NAME
ARG BUILD_REF
ARG BUILD_REPOSITORY
ARG BUILD_VERSION

# OCI + Home Assistant labels
LABEL \
    io.hass.name="${BUILD_NAME}" \
    io.hass.description="${BUILD_DESCRIPTION}" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="Guara92 <https://github.com/Guara92>" \
    org.opencontainers.image.title="${BUILD_NAME}" \
    org.opencontainers.image.description="${BUILD_DESCRIPTION}" \
    org.opencontainers.image.authors="Guara92 <https://github.com/Guara92>" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.url="https://github.com/${BUILD_REPOSITORY}" \
    org.opencontainers.image.source="https://github.com/${BUILD_REPOSITORY}" \
    org.opencontainers.image.documentation="https://github.com/${BUILD_REPOSITORY}/blob/main/numa/DOCS.md" \
    org.opencontainers.image.created=${BUILD_DATE} \
    org.opencontainers.image.revision=${BUILD_REF} \
    org.opencontainers.image.version=${BUILD_VERSION}
