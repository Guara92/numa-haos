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

Numa reads a single TOML file — `/config/numa.toml`. By default, this add-on
regenerates that file from the Home Assistant options panel on every start, so
the panel remains the source of truth. Set `config_source: file` if you want to
manage `/config/numa.toml` manually instead.

Dashboard-managed runtime state is stored separately and persists across
restarts, updates, and Home Assistant add-on backups under `/config/.config/numa/`.

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
| `notice` | Noteworthy events that are not warnings |
| `warning` | Non-fatal anomalies |
| `error` | Runtime errors only |
| `fatal` | Unrecoverable failures only |

### `config_source`

| Value | Behaviour |
|---|---|
| `default` | Regenerate `/config/numa.toml` from the add-on options on every start *(default)* |
| `file` | Use an existing `/config/numa.toml`; fail loudly if it is absent |

### `allow_from`

Optional CIDR/IP allowlist applied by Numa at every client-facing DNS surface,
including UDP/TCP DNS, DoT/DoH, and the `.numa` reverse proxy. Leave it empty to
keep Numa's upstream default of accepting all peers. If you expose port `53` or
`.numa` proxy ports beyond your trusted LAN, configure this.

Example:

```yaml
allow_from:
  - 192.168.0.0/16
  - 10.0.0.0/8
  - fd00::/8
```

### `rebind_protect`, `rebind_allowlist`, `rebind_private_ranges`

`rebind_protect` enables Numa's opt-in DNS rebinding protection introduced in
Numa `v0.21.0`. It strips private/special-use addresses from upstream answers so
a public domain cannot point clients at your router, NAS, Home Assistant host,
localhost, Tailscale/CGNAT ranges, ULA, or NAT64 addresses.

The add-on keeps this **disabled by default** to avoid breaking legitimate
split-horizon setups such as public hostnames that intentionally resolve to LAN
addresses. If you enable it, use `rebind_allowlist` for those domains. Leave
`rebind_private_ranges` empty unless you want to replace Numa's built-in ranges.

---

## `numa.toml` reference

All sections and keys are optional unless marked **required**.

### `[server]`

| Key | Type | Default | Notes |
|---|---|---|---|
| `bind_addr` | string | `"0.0.0.0:53"` | DNS listener `address:port` |
| `api_port` | integer | `5380` upstream; `5381` in this add-on | HTTP dashboard/API port |
| `api_bind_addr` | string | `"127.0.0.1"` | Main API stays loopback-only; bundled nginx handles HA Ingress |
| `data_dir` | string | `/var/lib/numa` upstream; `/data/numa` in this add-on | TLS CA/cert storage |
| `filter_aaaa` | bool | `false` | Answer AAAA queries with NODATA on IPv4-only networks |
| `allow_from` | array | `[]` | Optional CIDR/IP client allowlist for DNS, DoT/DoH, and `.numa` proxy |
| `rebind_protect` | bool | `false` | Strip private/special-use addresses from upstream answers |
| `rebind_allowlist` | array | `[]` | Domains exempt from rebinding protection |
| `rebind_private_ranges` | array | built-in ranges | Replacement CIDR set for rebinding protection |

> In this add-on, `api_bind_addr = "127.0.0.1"` is intentional. Home Assistant
> Ingress reaches Numa through the bundled nginx sidecar, so the unauthenticated
> Numa management API is not exposed directly on the LAN.

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
| `GET/PUT/POST` | `/blocking/*` | Toggle, pause, inspect allowlist, or manually block domains |
| `GET/PUT/POST` | `/rebind/*` | Inspect/toggle rebinding protection and manage its allowlist |
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
| `5381` | TCP | Internal dashboard / REST API behind bundled nginx Ingress proxy |
| `853` | TCP | DNS-over-TLS (optional, if `[dot] enabled = true`) |
| `80` / `443` | TCP | `.numa` proxy (optional, if `[proxy] enabled = true`) |

### Port 53 conflicts

Port `53` may already be occupied on Home Assistant OS by `systemd-resolved`
or another service. If the add-on fails to start with a
`bind: address already in use` error, stop and disable the conflicting
service before starting Numa.

### Ingress

The Numa dashboard is accessed through Home Assistant **Ingress** (the sidebar
entry) and does **not** require opening an additional firewall port under normal
use. The bundled nginx service listens on the Supervisor-assigned Ingress port
and proxies to Numa's loopback-only API at `127.0.0.1:5381`.

---

## Health monitoring & watchdog

The add-on intentionally does not configure the Home Assistant Supervisor HTTP
watchdog. With `host_network: true`, Supervisor would probe the Docker gateway,
while Numa's management API is intentionally bound to loopback only.

Instead, the image uses Docker's `HEALTHCHECK` against:

```text
GET http://127.0.0.1:5381/health
```

The endpoint returns HTTP 200 with `{"status":"ok","version":"…","uptime_secs":N,…}`
whenever Numa is running normally. The Supervisor can still react to container
state changes such as `UNHEALTHY`, `FAILED`, or `STOPPED`.

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
| `/config/.config/numa/*.json` | `/addon_configs/<repo>_numa/.config/numa/*.json` | Dashboard-managed services, manual blocklist/allowlist, rebind allowlist |

Configuration and dashboard-managed runtime lists survive add-on restarts, HA OS
upgrades, and add-on backups. TLS material lives under `/data/numa/`; the `/data/`
directory is excluded from backups by default because it contains auto-generated
TLS material that can be regenerated on first boot.

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

MIT License — Copyright (c) 2026 Guara92

[badge-repo]: https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg
[issue]: https://github.com/Guara92/numa-haos/issues
[my-repo]: https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FGuara92%2Fnuma-haos
[numa]: https://github.com/razvandimescu/numa
[numa-toml]: https://github.com/razvandimescu/numa/blob/main/numa.toml
[releases]: https://github.com/Guara92/numa-haos/releases
[semver]: https://semver.org/spec/v2.0.0.html
