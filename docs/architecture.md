# Numa — Architecture Overview

## Repository structure

```text
numa-haos/
├── repository.yaml              # HA App Store repository metadata
├── README.md                    # Repository-level documentation
├── LICENSE                      # MIT License
├── .gitignore
├── .github/
│   └── workflows/
│       ├── ci.yml               # Lint + build check on push / PR
│       └── release.yml          # Build + push multi-arch images on release
├── docs/
│   ├── architecture.md          # This file
│   ├── installation.md          # End-user installation guide
│   └── networking.md            # DNS / networking reference
└── numa/
    ├── config.yaml              # Supervisor app manifest
    ├── Dockerfile               # Container image definition
    ├── run.sh                   # App entrypoint (s6 / bashio)
    ├── numa.toml.default        # Default config written on first boot
    ├── README.md                # App-level README (shown in HA UI)
    ├── DOCS.md                  # Full app documentation
    ├── CHANGELOG.md             # Release history
    ├── apparmor.txt             # Custom AppArmor profile
    ├── icon.png                 # App icon (shown in HA App Store)
    ├── logo.png                 # App logo (shown on app page)
    ├── translations/
    │   └── en.yaml              # Human-readable labels for config options
    └── rootfs/                  # Files copied verbatim into the container image
        └── etc/
            └── numa/
                └── numa.toml.default   # Default config (accessible at runtime)
```

---

## Container runtime model (Phase 1 / Phase 2)

The first version uses a **single-process layout**: the container starts Numa
directly via `run.sh`, which is invoked by the Home Assistant Supervisor through
the s6-overlay init system bundled in the base image.

```text
┌─────────────────────────────────────────────────┐
│  Home Assistant Supervisor                       │
│                                                  │
│  ┌───────────────────────────────────────────┐   │
│  │  Numa App Container                        │   │
│  │                                            │   │
│  │  s6-overlay                                │   │
│  │    └── run.sh (bashio entrypoint)          │   │
│  │          └── /usr/local/bin/numa           │   │
│  │                ├── DNS listener  :53       │   │
│  │                └── Dashboard API :5380     │   │
│  │                                            │   │
│  │  Volumes:                                  │   │
│  │    /config  ← addon_config (numa.toml)     │   │
│  │    /data    ← addon data (TLS CA, state)   │   │
│  └───────────────────────────────────────────┘   │
│                                                  │
│  Ingress proxy ──── :5380 (dashboard/API)        │
│  Sidebar panel ─────────────────────────────►    │
└─────────────────────────────────────────────────┘
```

### Key points

- `host_network: true` is set in `config.yaml` so that Numa can bind to port
  `53` directly on the host interface — required for LAN-wide DNS.
- The dashboard on port `5380` is exposed through Home Assistant **Ingress**,
  not as a public port. Users access it from the HA sidebar without opening
  firewall rules.
- `run.sh` checks for the existence of `/config/numa.toml` on startup and
  writes the default config if it is absent (first-boot provisioning).

---

## Configuration model

```text
┌──────────────────────────────────────────┐
│  Home Assistant App Options (config.yaml) │
│  (log_level, dns_port, api_port, ...)     │
└──────────────────┬───────────────────────┘
                   │ read by run.sh via bashio::config
                   ▼
┌──────────────────────────────────────────┐
│  /config/numa.toml                        │
│  (full Numa configuration, TOML format)   │
│  Persisted via addon_config mapping       │
└──────────────────┬───────────────────────┘
                   │ positional argument
                   ▼
             /usr/local/bin/numa
```

The Home Assistant options (in `config.yaml`) control a small number of
runtime knobs exposed through the Supervisor UI. The full Numa configuration
lives in `numa.toml`, which is the source of truth for all DNS, proxy, cache,
and blocking settings.

This two-level model is intentional:

1. It avoids translating Numa's entire TOML schema into HA form fields (which
   would be brittle and hard to maintain).
2. It preserves Numa's native configuration model for users who want full
   control.
3. It keeps the Supervisor-facing options minimal and stable across Numa
   version upgrades.

---

## Ingress / dashboard access

Home Assistant Ingress proxies HTTP traffic from the sidebar panel to the
app container on `ingress_port` (default `5380`). The Supervisor injects an
`X-Ingress-Path` header so the app knows the base path prefix.

```text
Browser
  │
  │  https://<ha-host>/api/hassio_ingress/<token>/
  ▼
Home Assistant Supervisor Ingress Proxy
  │
  │  http://127.0.0.1:5380/
  ▼
Numa Dashboard (API port inside container)
```

If Numa's dashboard does not handle the Ingress path prefix correctly, assets
(JS/CSS) may fail to load. This is flagged as a **technical risk** and should
be validated during the Phase 0 spike.

---

## Multi-arch build strategy

The Dockerfile uses the `BUILD_ARCH` build argument to select the correct
binary to download for each target architecture:

| `BUILD_ARCH` | Docker platform | Numa binary suffix |
|---|---|---|
| `aarch64` | `linux/arm64` | `aarch64` |
| `amd64` | `linux/amd64` | `x86_64` |

CI builds are triggered on every push and pull request. Release builds
publish multi-arch images to the GitHub Container Registry (GHCR) under
`ghcr.io/guara92/numa-<arch>:<version>`.

---

## Planned evolution (later phases)

### Phase 4 — Minimal TOML editor

A small helper HTTP service will be added to the container alongside Numa.
This service will:

- serve a minimal web page (textarea + Save + Restart buttons) through Ingress;
- read and write `/config/numa.toml`;
- trigger a Numa process reload or restart after a save.

The runtime model will evolve to a **two-process layout** supervised by s6:

```text
s6-overlay
  ├── numa         (DNS service)
  └── editor       (tiny HTTP helper, e.g. a small Go or Python service)
```

The `ingress_port` will point to the editor process, which will reverse-proxy
to the Numa dashboard for all non-editor routes.

### Future — Custom integration (optional)

If Home Assistant entities (sensors, switches, buttons) are added in the
future, a `custom_components/numa/` directory can be added to this repository
or created in a separate repository. This is explicitly out of scope for v1.
