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
    ├── config.yaml              # Supervisor add-on manifest + options schema
    ├── Dockerfile               # HA base image + downloaded upstream Numa binary
    ├── README.md                # Add-on card README
    ├── DOCS.md                  # Full add-on documentation
    ├── CHANGELOG.md             # Release history
    ├── apparmor.txt             # Custom AppArmor profile
    ├── icon.png / logo.png      # HA add-on store assets
    └── rootfs/                  # Files copied into the container image
        └── etc/
            ├── nginx/           # Ingress reverse-proxy config/templates
            └── s6-overlay/      # init-numa, init-nginx, numa, nginx services
```

---

## Container runtime model

The add-on uses the `ghcr.io/hassio-addons/base` image and s6-overlay. Numa and
nginx run as separate supervised services; nginx exists only to adapt Numa's
loopback dashboard/API to Home Assistant Ingress.

```text
┌─────────────────────────────────────────────────────────┐
│  Home Assistant Supervisor                               │
│                                                         │
│  Sidebar / Open Web UI                                  │
│          │                                              │
│          ▼                                              │
│  Supervisor Ingress ──► nginx :<ingress_port>           │
│                              │                          │
│                              ▼                          │
│                       Numa API 127.0.0.1:5381           │
│                                                         │
│  LAN clients ─────────► Numa DNS :53 UDP/TCP            │
│  LAN DoT clients ─────► Numa DoT :853                   │
│  Mobile onboarding ───► Numa mobile API :8765           │
└─────────────────────────────────────────────────────────┘
```

### Key points

- `host_network: true` is set in `config.yaml` so Numa can bind to port `53`
  directly on the Home Assistant host interface.
- Numa's main dashboard/API binds to `127.0.0.1:5381`; it is intentionally not
  exposed directly on the LAN.
- nginx listens on the Supervisor-assigned Ingress port and proxies to
  `127.0.0.1:5381`, including dashboard asset/path rewrites needed by Ingress.
- Docker `HEALTHCHECK` probes `http://127.0.0.1:5381/health`; the Supervisor HTTP
  watchdog is intentionally omitted because it cannot reach loopback correctly in
  this host-network topology.

---

## Configuration model

```text
┌──────────────────────────────────────────┐
│  Home Assistant App Options (config.yaml) │
│  (DNS, upstream, blocking, proxy, etc.)   │
└──────────────────┬───────────────────────┘
                   │ read by init-numa via bashio + jq
                   ▼
┌──────────────────────────────────────────┐
│  /config/numa.toml                        │
│  (generated unless config_source=file)     │
│  Persisted via addon_config mapping       │
└──────────────────┬───────────────────────┘
                   │ positional argument
                   ▼
             /usr/local/bin/numa
```

By default, `init-numa` regenerates `/config/numa.toml` from the Home Assistant
options on every start. This keeps the Supervisor UI as the source of truth for
normal operation. Setting `config_source: file` switches to manual TOML mode and
makes `/config/numa.toml` the source of truth.

Dashboard-managed runtime state is separate from `numa.toml`: services,
manual blocklist/allowlist entries, and the rebind allowlist are persisted by
Numa as JSON under `/config/.config/numa/`. The `numa` service exports
`HOME=/config` before launch so upstream Numa's `config_dir()` resolves into the
persistent `addon_config` mapping instead of container-local `/var/lib/numa`.

---

## Ingress / dashboard access

Home Assistant Ingress proxies HTTP traffic from the sidebar panel to the add-on
container on the Supervisor-assigned `ingress_port`. The bundled nginx server
then proxies to Numa's loopback API on `127.0.0.1:5381`.

```text
Browser
  │
  │  https://<ha-host>/api/hassio_ingress/<token>/
  ▼
Home Assistant Supervisor Ingress Proxy
  │
  │  http://<addon-ip>:<ingress_port>/
  ▼
nginx ingress server
  │
  │  http://127.0.0.1:5381/
  ▼
Numa Dashboard/API
```

nginx rewrites the dashboard's API base path and absolute `/fonts/...` asset
URLs using the `X-Ingress-Path` header injected by Home Assistant.

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
