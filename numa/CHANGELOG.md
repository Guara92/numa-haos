# Changelog

## [0.3.0]

### Changed

- Bumped upstream Numa binary from **v0.13.1 → v0.14.0**.
  All source files are identical between the two releases; v0.14.0 is a
  documentation, packaging and config-schema release. No behavioural changes
  to DNS resolution, blocking or the API.

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
