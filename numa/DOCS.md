# Home Assistant Add-on: Numa

[Numa][numa] is a self-hosted DNS resolver written from scratch in Rust — zero
external DNS libraries, RFC 1035 wire protocol hand-parsed. It combines DNS
forwarding, ad blocking (385 K+ Hagezi Pro domains), DNS-over-HTTPS/TLS,
DNSSEC validation, a `.numa` local service proxy with auto-TLS, LAN mDNS
discovery, and a REST API with a web dashboard — all in a single ~8 MB binary.

---

## Installation

1. Add this repository to your Home Assistant instance:

   [![Open your Home Assistant instance and show the add add-on repository
   dialog with a specific repository URL pre-filled.][badge-repo]][my-repo]

1. Find **Numa** in the add-on store and click **Install**.
1. Start the add-on and open the **Log** tab to confirm a successful startup.
1. Click **OPEN WEB UI** or the **Numa** sidebar entry to reach the dashboard.

> **Before pointing your router or devices at Numa for DNS**, make sure the
> Home Assistant host has a **static IP address**. A dynamic DHCP lease will
> cause DNS failures for every device on your network after a lease renewal.

---

## Configuration

Numa is configured entirely through a single TOML file — `numa.toml`. On first
boot the add-on writes a sensible default to the persistent config location.
All subsequent restarts read that file directly; the add-on options panel in
Home Assistant only controls a small number of operational settings.

### Persistent config path

| Inside the container | Host path (approximate) |
|---|---|
| `/config/numa.toml` | `/addon_configs/<repo>_numa/numa.toml` |
| `/data/numa/` | Add-on data directory |

Edit `/config/numa.toml` with the **File editor** add-on, the **SSH** add-on,
or any other editor that can reach the HA config directory. **Restart the
add-on after every change** — Numa loads its configuration once at startup
and there is no live-reload signal.

---

## Add-on options

### `log_level`

Controls the verbosity of the add-on log output. The value is forwarded to
Numa via the `RUST_LOG` environment variable, which Numa's `env_logger`
backend reads directly.

| Value | Meaning |
|---|---|
| `trace` | Every internal function call |
| `debug` | Detailed debug information |
| `info` | Normal operational events *(default)* |
| `warning` | Non-fatal anomalies |
| `error` | Runtime errors only |
| `fatal` | Unrecoverable failures only |

### `dns_port`

The UDP/TCP port Numa listens on for DNS queries.

- **Default:** `53`
- Only change this if port `53` is already in use on the host (e.g. by
  `systemd-resolved`). If you do change it, update `bind_addr` in
  `numa.toml` accordingly.

### `api_port`

The HTTP port for the Numa dashboard and REST API inside the container.

- **Default:** `5380`
- This port is proxied through Home Assistant Ingress. You do not normally
  need to open it in your firewall.
- If you change it here, also change `api_port` in `numa.toml` to match.

### `config_source`

| Value | Behaviour |
|---|---|
| `default` | Write `numa.toml` from the embedded template on first boot *(default)* |
| `file` | Expect an existing `numa.toml`; fail loudly if it is absent |

---

## `numa.toml` reference

All sections and keys are optional unless marked **required**.

### `[server]`

| Key | Type | Default | Notes |
|---|---|---|---|
| `bind_addr` | string | `"0.0.0.0:53"` | DNS listener `address:port` |
| `api_port` | integer | `5380` | HTTP dashboard/API port |
| `api_bind_addr` | string | `"127.0.0.1"` | **Must be `"0.0.0.0"`** for HA Ingress to reach the dashboard |
| `data_dir` | string | `/var/lib/numa` | TLS CA/cert storage; set to `"/data/numa"` in the add-on |
| `filter_aaaa` | bool | `false` | Answer AAAA queries with NODATA on IPv4-only networks |

> **`api_bind_addr = "0.0.0.0"` is required** in the Home Assistant add-on.
> The default `"127.0.0.1"` restricts the dashboard to loopback only, which
> prevents the HA Ingress proxy from reaching it.

### `[upstream]`

| Key | Type | Default | Notes |
|---|---|---|---|
| `mode` | string | `"forward"` | `"forward"`, `"recursive"`, or `"auto"` |
| `address` | string \| array | — | Upstream DNS. Supports plain UDP (`9.9.9.9`), DoH (`https://…`), DoT (`tls://IP#hostname`) |
| `fallback` | array | — | Tried only when all primaries fail |
| `timeout_ms` | integer | `3000` | Per-query timeout |
| `hedge_ms` | integer | `10` | Parallel rescue delay; `0` disables hedging |

### `[[forwarding]]` *(repeatable)*

Per-suffix conditional forwarding (split-horizon DNS):

```toml
[[forwarding]]
suffix   = "home.arpa"
upstream = "192.168.1.1"
```

### `[blocking]`

| Key | Type | Default | Notes |
|---|---|---|---|
| `enabled` | bool | `true` | Enable ad blocking |
| `refresh_hours` | integer | `24` | Blocklist refresh interval |
| `lists` | array | Hagezi Pro URL | URLs of hosts-format blocklists |
| `allowlist` | array | `[]` | Domains that are never blocked |

### `[cache]`

| Key | Type | Default | Notes |
|---|---|---|---|
| `max_entries` | integer | `100000` | Maximum cached DNS records |
| `min_ttl` | integer | `60` | TTL floor in seconds |
| `max_ttl` | integer | `86400` | TTL ceiling in seconds |
| `warm` | array | — | Domains to pre-resolve at startup |

### `[proxy]`

The `.numa` local service proxy gives any local service a TLS-backed
`<name>.numa` hostname with auto-generated certificates.

| Key | Type | Default | Notes |
|---|---|---|---|
| `enabled` | bool | `true` | Enable the proxy |
| `port` | integer | `80` | HTTP proxy port |
| `tls_port` | integer | `443` | HTTPS proxy port |
| `tld` | string | `"numa"` | Local TLD |
| `bind_addr` | string | `"127.0.0.1"` | Set `"0.0.0.0"` to expose proxy on LAN |

Register services under the proxy:

```toml
[[services]]
name        = "homeassistant"
target_port = 8123
```

### `[[zones]]` *(repeatable)*

Static DNS overrides:

```toml
[[zones]]
domain      = "homeassistant.local"
record_type = "A"
value       = "192.168.1.10"
ttl         = 60
```

### `[dot]`

DNS-over-TLS listener (RFC 7858). Numa generates a self-signed CA
automatically; download `/ca.pem` from the dashboard and install it on
clients to trust the certificate.

| Key | Type | Default | Notes |
|---|---|---|---|
| `enabled` | bool | `true` | Enable DoT listener |
| `port` | integer | `853` | DoT port |
| `bind_addr` | string | `"0.0.0.0"` | Bind address |
| `cert_path` | string | — | PEM cert; omit to use auto-generated self-signed cert |
| `key_path` | string | — | PEM key; must pair with `cert_path` |

### `[dnssec]`

DNSSEC chain-of-trust validation. Requires `mode = "recursive"` in
`[upstream]`.

| Key | Type | Default | Notes |
|---|---|---|---|
| `enabled` | bool | `false` | Enable DNSSEC validation |
| `strict` | bool | `false` | Return `SERVFAIL` for bogus signatures |

### `[lan]`

LAN mDNS peer discovery (`_numa._tcp.local`).

| Key | Type | Default | Notes |
|---|---|---|---|
| `enabled` | bool | `false` | Enable LAN discovery |
| `broadcast_interval_secs` | integer | `30` | mDNS broadcast interval |
| `peer_timeout_secs` | integer | `90` | Time before a peer is removed |

---

## REST API

Numa exposes a REST API on `api_port` (default `5380`). All responses are
JSON. The dashboard itself is served at `GET /`.

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check — always returns `{"status":"ok",…}` |
| `GET` | `/stats` | Full statistics object |
| `GET` | `/query-log` | Recent DNS query log |
| `GET/DELETE` | `/cache` | Inspect or flush the DNS cache |
| `GET/POST/DELETE` | `/overrides` | Temporary DNS overrides |
| `GET` | `/diagnose/{domain}` | Step-by-step resolution trace |
| `GET/PUT/POST` | `/blocking/*` | Toggle, pause, or inspect the blocklist |
| `GET/POST/DELETE` | `/services` | Manage `.numa` proxy services |
| `GET` | `/ca.pem` | Download the auto-generated CA certificate |

---

## Networking

This add-on uses **host networking** so that Numa can bind directly to
port `53` on the Home Assistant host interface — a requirement for acting as
a real network-level DNS server.

### Port reference

| Port | Protocol | Purpose |
|---|---|---|
| `53` | UDP + TCP | DNS queries from clients |
| `5380` | TCP | Dashboard / REST API (Ingress only by default) |
| `853` | TCP | DNS-over-TLS (optional, if `[dot] enabled = true`) |
| `80` / `443` | TCP | `.numa` proxy (optional, if `[proxy] enabled = true`) |

### Port 53 conflicts

Port `53` may already be occupied on Home Assistant OS by `systemd-resolved`
or another service. If the add-on fails to start with a
`bind: address already in use` error, stop and disable the conflicting
service before starting Numa.

### Ingress

The Numa dashboard is accessed through Home Assistant **Ingress** (the sidebar
entry) and does **not** require opening an additional firewall port under
normal use. The `api_bind_addr = "0.0.0.0"` setting in `numa.toml` is
required for the Ingress proxy to reach the dashboard.

---

## Health monitoring & watchdog

Home Assistant monitors the add-on via the Numa health endpoint:

```text
GET http://<host>:5380/health
```

The endpoint returns HTTP 200 with `{"status":"ok","version":"…","uptime_secs":N,…}`
whenever Numa is running normally. If the endpoint stops responding, the
Supervisor will automatically restart the add-on.

---

## Security

This add-on ships with a custom **AppArmor** profile (`apparmor.txt`) that
confines the Numa process to only the paths and capabilities it actually
needs:

- **`CAP_NET_BIND_SERVICE`** — bind to privileged ports 53 and 853
- Read/write access to `/config/numa.toml` and `/data/numa/`
- Network access for upstream DNS queries and TLS connections
- No access to the HA config directory, host devices, or kernel interfaces

The resulting security score is **6/6**
(base 5 + 2 Ingress − 1 host network + 1 custom AppArmor).

---

## Persistent storage

| Container path | Host path (approximate) | Contents |
|---|---|---|
| `/config/numa.toml` | `/addon_configs/<repo>_numa/numa.toml` | Main configuration |
| `/data/numa/` | Add-on data directory | TLS CA, certs, internal state |

Configuration and TLS material survive add-on restarts and HA OS upgrades.
The `/data/` directory is excluded from backups by default because it contains
auto-generated TLS material that can be regenerated on first boot.

---

## Changelog & Releases

This repository follows [Semantic Versioning][semver]: `MAJOR.MINOR.PATCH`.
Releases and changelogs are maintained on the [GitHub Releases page][releases].

---

## Support

- [Open an issue on GitHub][issue]
- [Numa upstream repository][numa]
- [Numa `numa.toml` sample file][numa-toml]

---

## License

MIT License — Copyright (c) 2024 Guara92

[badge-repo]: https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg
[issue]: https://github.com/Guara92/numa-haos/issues
[my-repo]: https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FGuara92%2Fnuma-haos
[numa]: https://github.com/razvandimescu/numa
[numa-toml]: https://github.com/razvandimescu/numa/blob/main/numa.toml
[releases]: https://github.com/Guara92/numa-haos/releases
[semver]: https://semver.org/spec/v2.0.0.html
