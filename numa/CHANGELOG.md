# Changelog

## [0.12.0]

### Changed

- Bumped upstream Numa binary from **v0.20.0 → v0.21.0**.

## [0.11.0]

### Changed

- Bumped upstream Numa binary from **v0.19.0 → v0.20.0**.

## [0.10.0]

### Changed

- Bumped upstream Numa binary from **v0.18.0 → v0.19.0**.

## [0.9.0]

### Changed

- Bumped upstream Numa binary from **v0.17.0 → v0.18.0**.

## [0.8.0]

### Changed

- Bumped upstream Numa binary from **v0.16.0 → v0.17.0**.

## [0.7.0]

### Changed

- Bumped upstream Numa binary from **v0.15.1 → v0.16.0**.

## [0.6.0]

### Added

- Full configuration panel: all `numa.toml` fields are now exposed as add-on
  options — upstream mode, hedging, ODoH, blocking, cache, proxy, DNS-over-TLS,
  DNSSEC, LAN peer discovery, mobile onboarding, split-horizon forwarding rules,
  and static DNS zones.
- `init-numa` oneshot s6-overlay service: config generation and network readiness
  check are now separated from the main Numa process, following s6 best practice.
- DoT (port `853/tcp`) and mobile onboarding (port `8765/tcp`) advertised in the
  add-on manifest so HA surfaces them in the Network tab.
- `repository.json` added so the repo can be added as a custom HA add-on store.

### Changed

- Bumped upstream Numa binary from **v0.14.3 → v0.15.1**.
- `upstream_hedge_ms` default changed from `10` → `50` ms. At 10 ms hedging
  fired on nearly every query (normal upstream latency 8–20 ms); 50 ms targets
  only genuinely stalled responses and avoids doubling query counts routinely.

## [0.5.1]

### Changed

- Fixed networking check in run script.

## [0.5.0]

### Changed

- Bumped upstream Numa binary from **v0.14.2 → v0.14.3**.
- Dockerfile SHA-256 integrity check added for the Numa binary tarball.

## [0.4.0]

### Changed

- Bumped upstream Numa binary from **v0.14.1 → v0.14.2**.
- Minor updates to default config

## [0.3.0]

### Changed

- Bumped upstream Numa binary from **v0.13.1 → v0.14.1**.

### Added

- `filter_aaaa` option documented in `numa.toml.default`: answers AAAA queries
  with NODATA on IPv4-only networks so Happy Eyeballs clients don't stall, and
  strips `ipv6hint` from HTTPS/SVCB records (RFC 9460).
- ODoH (Oblivious DNS over HTTPS, RFC 9230) example block added to
  `numa.toml.default` (commented out). Includes `relay_ip` / `target_ip`
  bootstrap-IP fields introduced in v0.14.0 that break the circular DNS
  dependency when this add-on is itself the LAN DNS server.
- Array-of-upstreams example for `[[forwarding]]` rules in `numa.toml.default`;
  Numa performs SRTT-aware failover across all listed upstreams.

### Fixed

- Startup network readiness check now runs in **two phases** before handing
  control to Numa:
  1. **Phase 1** (existing) — probes Quad9 by hardcoded IP to confirm outbound
     TCP/TLS/HTTP connectivity without relying on DNS.
  2. **Circular-DNS fix** — prepends `nameserver 9.9.9.9` to the container's
     `/etc/resolv.conf` (Docker mount namespace keeps this local to the
     container; the host and LAN DHCP clients are unaffected). This breaks the
     chicken-and-egg where `getaddrinfo()` inside `reqwest` would query Numa's
     own port 53 before Numa's UDP listener loop has started.
  3. **Phase 2** — validates that the system resolver can now reach
     `cdn.jsdelivr.net` (the blocklist CDN) using a lightweight `HEAD` request,
     confirming the fix worked before Numa is exec'd.
- Reduced `refresh_hours` default from 24 h to 6 h in `numa.toml.default` so a
  startup failure recovers sooner on new installs.

## [0.1.0] — Initial release

### Added

- Initial release of the Numa Home Assistant Add-on.
- Multi-arch container image support for `aarch64` and `amd64`.
- Home Assistant Ingress support for sidebar dashboard access.
- Persistent `numa.toml` configuration via `addon_config` mapping.
- Default sample `numa.toml` written on first boot if none exists.
- DNS service on port `53` (UDP/TCP) via host network.
- Add-on configuration options: `log_level`, `config_source`.

[Unreleased]: https://github.com/Guara92/numa-haos/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Guara92/numa-haos/releases/tag/v0.1.0
