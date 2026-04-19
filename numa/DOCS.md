# Home Assistant App: Numa

[Numa][numa] is a self-hosted DNS resolver with a built-in dashboard, ad
blocking, DNS-over-HTTPS/TLS, and a local `.numa` proxy for your home services.

## Installation

1. Add this repository to your Home Assistant instance:

   [![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FGuara92%2Fnuma-haos)

1. Find the **Numa** app in the add-on store and click **Install**.
1. Start the app and check the logs to confirm it started correctly.
1. Click **OPEN WEB UI** or the sidebar entry to access the Numa dashboard.

> **Important**: Before pointing your router or devices at Numa for DNS,
> make sure your Home Assistant host has a **static IP address**. A dynamic
> IP will cause DNS failures after a DHCP lease renewal.

## Configuration

After the first start, a default `numa.toml` is written to the persistent
config location (`/config/numa/numa.toml` on the host). You can edit this
file directly via the Filesystem editor, SSH, or the built-in TOML editor
(Phase 4, coming soon).

**Remember to restart the app after any configuration change.**

### Option: `log_level`

Controls verbosity of the app log output. Possible values:

- `trace` — every internal call
- `debug` — detailed debug information
- `info` — normal operational events *(default)*
- `warning` — non-fatal anomalies
- `error` — runtime errors
- `fatal` — unrecoverable failures

### Option: `dns_port`

The UDP/TCP port Numa listens on for DNS queries.

- Default: `53`
- Change this only if port `53` is already in use on your host.

### Option: `api_port`

The HTTP port for the Numa dashboard and API inside the container.

- Default: `5380`
- This port is proxied through Home Assistant Ingress; you normally do not need
  to expose it directly.


## Networking notes

This app uses **host networking** so that Numa can bind directly to port `53`
on the Home Assistant host interface. This is required for Numa to act as a
real DNS server for your local network.

If port `53` is already occupied (e.g. by `systemd-resolved` or another DNS
service), the app will fail to start. Check the add-on logs for a
`bind: address already in use` error and stop/disable the conflicting service
first.

The Numa dashboard is accessed through Home Assistant **Ingress** (the sidebar
entry) and does **not** require opening an additional firewall port under
normal use.

## Persistent storage

Numa stores its configuration and data in two mapped paths:

| Container path | Host path (approximate) | Purpose |
|---|---|---|
| `/config/numa` | `/config/numa/` | `numa.toml` and user config |
| `/data` | Add-on data directory | TLS CA material, internal state |

Configuration survives app restarts and Home Assistant OS upgrades.

## TOML configuration reference

The full `numa.toml` reference is maintained upstream:

- [numa.toml sample file][numa-toml]
- [Numa repository][numa]

A minimal working configuration for Home Assistant OS:

```toml
[server]
bind_addr = "0.0.0.0:53"
api_port = 5380

[cache]
max_entries = 100000
min_ttl = 60
max_ttl = 86400

[proxy]
enabled = true
port = 80
tls_port = 443
tld = "numa"
```

## Changelog & Releases

This repository keeps a change log using [GitHub's releases][releases]
functionality.

Releases follow [Semantic Versioning][semver]: `MAJOR.MINOR.PATCH`.

## Support

- [Open an issue on GitHub][issue]
- [Numa upstream repository][numa]

## License

MIT License — Copyright (c) 2024 Guara92

[issue]: https://github.com/Guara92/numa-haos/issues
[numa]: https://github.com/razvandimescu/numa
[numa-toml]: https://github.com/razvandimescu/numa/blob/main/numa.toml
[releases]: https://github.com/Guara92/numa-haos/releases
[semver]: https://semver.org/spec/v2.0.0.html