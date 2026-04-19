# Numa — Networking Guide

## Overview

Numa binds to two ports by default:

| Port | Protocol | Purpose |
|------|----------|---------|
| 53 | UDP/TCP | DNS resolver |
| 5380 | TCP | Dashboard / API |

When running as a Home Assistant app, the dashboard is exposed through
**Ingress** (no direct public port needed). The DNS port `53` requires
`host_network: true` to be reachable from the rest of your local network.

---

## Host Networking

The app runs with `host_network: true`. This means Numa binds directly to the
host's network interfaces, which is required for DNS to work correctly on
port `53`.

### Implications

- Numa's DNS listener (`0.0.0.0:53`) will be reachable from any device on
  your LAN that points to the Home Assistant OS IP.
- No port mapping is required for DNS — it binds to the host directly.
- The dashboard is served through Home Assistant Ingress and is **not**
  exposed on a public port by default.

---

## Static IP requirement

> **Important**: Your Home Assistant device **must** have a static IP address
> for DNS to work reliably.

If the IP of your Home Assistant instance changes, all devices using it as
their DNS server will lose resolution.

Configure a static IP in Home Assistant:

1. Go to **Settings → System → Network**
2. Select your network interface
3. Set IPv4 to **Static**
4. Enter your IP address, subnet mask, and gateway

Alternatively, assign a static lease in your router's DHCP settings using the
device's MAC address.

---

## Static external DNS servers

> **Important**: You must also set static external DNS servers on the Home
> Assistant device itself.

If you point your Home Assistant OS device to itself (`127.0.0.1`) as DNS
before Numa is running, it may fail to resolve hostnames at startup (e.g.,
for pulling container images or reaching the internet).

Recommended approach:

- Set a reliable external DNS on the HA OS network interface
  (e.g., `9.9.9.9` or `1.1.1.1`).
- Let Numa handle DNS for *other devices* on your LAN by pointing their DNS
  to the HA OS static IP.
- Do **not** point the HA OS device itself to Numa unless you are confident
  Numa is always running before HA needs DNS.

---

## Port 53 conflict

On some systems, another process may already be listening on port `53`
(e.g., `systemd-resolved`). On Home Assistant OS this is unlikely, but if
you see a startup error like:

```text
bind: address already in use
```

Check which process owns port 53:

```sh
ss -tulpn | grep ':53'
```

Home Assistant OS does not run `systemd-resolved` by default, so this should
not be an issue in standard installations.

---

## Ingress and the dashboard

The Numa dashboard (API port `5380`) is proxied through Home Assistant
Ingress. This means:

- You access it via the Home Assistant sidebar — no separate port to open on
  your firewall.
- The dashboard is protected by your Home Assistant authentication.
- Direct access on port `5380` is also available if you need it (e.g., for
  scripting or testing).

### Ingress path prefix

Home Assistant Ingress rewrites requests with a path prefix. Numa's dashboard
must be able to serve assets correctly under this prefix. If you notice the
dashboard loading without CSS or JavaScript, this is the likely cause —
check the `ingress_entry` option in the app configuration.

---

## DNS-over-TLS (DoT)

Numa supports DNS-over-TLS on port `853`. This is disabled by default.
To enable it, add the following to your `numa.toml`:

```toml
[dot]
enabled = true
port = 853
bind_addr = "0.0.0.0"
```

If you enable DoT, you may also want to expose port `853` in the app
configuration or rely on the host network binding.

---

## Conditional forwarding

If you have other local DNS servers (e.g., Pi-hole, Unbound, or a router
running DNS), you can configure per-suffix forwarding rules in `numa.toml`:

```toml
[[forwarding]]
suffix = "home.arpa"
upstream = "192.168.1.1"

[[forwarding]]
suffix = "local"
upstream = "192.168.1.1"
```

This allows Numa to forward local zone queries to your existing DNS while
resolving everything else upstream.

---

## Firewall recommendations

For a typical home setup:

| Direction | Port | Protocol | Action |
|-----------|------|----------|--------|
| LAN → HA OS | 53 | UDP | Allow |
| LAN → HA OS | 53 | TCP | Allow |
| LAN → HA OS | 853 | TCP | Allow (optional, DoT) |
| WAN → HA OS | 53 | UDP/TCP | Block (do not expose DNS publicly) |

The Home Assistant Ingress dashboard port does not need to be opened — it is
handled internally by the Supervisor.
