# Numa HAOS — 3000ms Forward Latency Investigation

## Status: IN PROGRESS — Root cause not yet confirmed

---

## Symptom

All non-cached DNS queries show `FORWARD` path at exactly `~3000ms` in the Numa dashboard query log:

```
FORWARD        3092ms  ping.archlinux.org
FORWARD        3096ms  push.services.mozilla.com
FORWARD        3083ms  push.services.mozilla.com
FORWARD        3093ms  signaler-pa.clients6.google.com
FORWARD        3077ms  www.youtube.com
FORWARD        3095ms  lin-efz.ms-acdc.office.com
FORWARD        3064ms  clients3.google.com
CACHED            0ms  www.google.com
```

The latency value (~3000ms) matches exactly the `timeout_ms = 3000` set in the running `/addon_configs/ee660d3e_numa/numa.toml`.

---

## Environment

| Item | Value |
|---|---|
| HA add-on | `ee660d3e_numa` |
| Config path (actual) | `/addon_configs/ee660d3e_numa/numa.toml` |
| Config path (mounted) | `/config/numa.toml` inside container |
| `/etc/resolv.conf` | `nameserver 192.168.1.1`, two ULA IPv6 nameservers, **no search/domain lines** |
| System DNS (resolvectl) | `192.168.1.1` (router) |
| IPv6 | Working — `ping6 2620:fe::fe` alive |
| Quad9 DoH direct test | HTTP 400 in **67ms** — DoH itself is fast and reachable |

---

## Key Finding: FORWARD ≠ UPSTREAM (confirmed from source code)

From `src/stats.rs`:

```rust
QueryPath::Forwarded => "FORWARD",   // [[forwarding]] suffix rules
QueryPath::Upstream  => "UPSTREAM",  // main [upstream] pool (Quad9 DoH)
```

From `src/ctx.rs` (resolution pipeline):

```rust
// Branch 1 — [[forwarding]] rules → produces "FORWARD"
} else if let Some(pool) =
    crate::system_dns::match_forwarding_rule(&qname, &ctx.forwarding_rules)
{
    forward_with_failover_raw(...)
    (resp, QueryPath::Forwarded, ...)

// Branch 2 — main [upstream] pool → produces "UPSTREAM"
} else {
    let pool = ctx.upstream_pool.lock().unwrap().clone();
    forward_with_failover_raw(...)
    (resp, QueryPath::Upstream, ...)
}
```

**The 3000ms latency has nothing to do with Quad9 DoH.** The queries are hitting `[[forwarding]]` rules whose upstream is timing out.

---

## Running Config (the actual file Numa is loading)

```toml
[upstream]
mode    = "forward"
address = ["https://dns.quad9.net/dns-query", "tls://9.9.9.9#dns.quad9.net", "tls://149.112.112.112#dns.quad9.net"]
# [[forwarding]]         ← ALL COMMENTED OUT
# suffix   = ["home.arpa", "local"]
# upstream = "127.0.0.1"
```

**This config has no active `[[forwarding]]` rules.** Yet ALL queries show `FORWARD` path.

`curl -s http://127.0.0.1:5381/stats` reports:

```
upstream : https://dns.quad9.net/dns-query (+4 more)
config   : /config/numa.toml
mode     : ?   ← upstream_mode field absent from this Numa version's /stats response
```

The `+4 more` means Numa sees 5 upstreams total: 1 DoH + 2 DoT + 2 UDP fallbacks.

---

## Why FORWARD path despite no [[forwarding]] rules — UNRESOLVED

### What auto-discovery does (from `src/system_dns.rs`)

On Linux, `discover_linux()` reads `/etc/resolv.conf`:
- Extracts first non-loopback nameserver → `default_upstream = Some("192.168.1.1")`
- Extracts `search`/`domain` lines → **none present** → `forwarding_rules = []`

Since there are no search domains, **zero forwarding rules are auto-created**.

### What `serve.rs` does at startup

```rust
// Forward mode with explicit address= → uses configured addresses, NOT system DNS
let addrs = if config.upstream.address.is_empty() {
    vec![detected_system_dns]   // ← NOT taken (address is non-empty)
} else {
    config.upstream.address.clone()  // ← Quad9 DoH + DoT used
};

// Merge config [[forwarding]] rules + auto-discovered rules
let forwarding_rules =
    crate::config::merge_forwarding_rules(&config.forwarding, system_dns.forwarding_rules)?;
// = [] + [] = []
```

With `forwarding_rules = []`, `match_forwarding_rule` should **never** return `Some`, so queries should go to `UPSTREAM` path. Yet they show `FORWARD`.

### Contradiction

The code path and the observed data are irreconcilable given the known config. Either:

1. The config that Numa actually loaded at runtime is **different from what `grep` showed** (e.g. a stale in-memory state from a previous run before restart, or the file was modified after Numa started), OR
2. There is a **code path in `serve.rs` not yet identified** that populates `forwarding_rules` from the DoT/DoH upstreams or system DNS even when `address` is non-empty, OR
3. The `network_watch_loop` in `serve.rs` is somehow injecting forwarding rules at runtime (currently only confirmed to update `upstream_pool`, not `forwarding_rules`), OR
4. The Numa binary running is a **different version** than v0.13.1 whose source we read.

---

## Failover is Sequential (confirmed from source code)

From `src/forward.rs`:

```rust
pub async fn forward_with_failover_raw(...) {
    // Sort by SRTT — DoH always sorts first (tracked_ip() = None → rtt = 0)
    candidates.sort_by_key(|&(_, rtt)| rtt);

    // Try upstreams ONE BY ONE — NOT in parallel
    for upstream in &all_upstreams {
        let result = forward_with_hedging_raw(wire, upstream, upstream, ...).await;
        match result {
            Ok(resp) => return Ok(resp),   // first success wins
            Err(e) => { last_err = Some(e); continue; }  // try next on failure
        }
    }
}
```

`hedge_ms` fires a parallel request to the **same** upstream (rescues UDP packet loss). It does NOT fire to a different upstream. Upstreams are tried sequentially.

**DoH upstreams are NOT tracked by SRTT** (`tracked_ip()` returns `None` for DoH). They always sort first (rtt=0) and are always tried before DoT/UDP upstreams.

---

## DoT Still Present in Running Config

The running config still has the old DoT upstreams:

```toml
address = ["https://dns.quad9.net/dns-query", "tls://9.9.9.9#dns.quad9.net", "tls://149.112.112.112#dns.quad9.net"]
timeout_ms = 3000   ← not yet updated to 800
```

The updated `numa.toml.default` (not yet applied to HA) removes DoT and sets `timeout_ms = 800`.

---

## Changes Made (in repo, NOT YET applied to HA)

### `numa/rootfs/etc/numa/numa.toml.default`

| Setting | Old | New | Reason |
|---|---|---|---|
| `address` | DoH Quad9 + DoT×2 | DoH Quad9 + DoH Cloudflare | Port 853 (DoT) often silently dropped |
| `timeout_ms` | `3000` | `800` | 3 s = exact symptom; fail fast so SRTT routes around bad upstreams |
| `warm` | `dns.quad9.net` | + `cloudflare-dns.com` | Pre-resolve both DoH upstreams |

### `numa/rootfs/etc/nginx/templates/ingress.gtpl`

Added `sub_filter` rules to rewrite absolute `/fonts/` paths (both in HTML and CSS) through the HA ingress prefix. Without this, `fonts.css` and all `.woff2` files 404.

---

## Next Steps

### To close the FORWARD path mystery:

1. **Restart the add-on** and immediately capture the startup banner (increase log level to INFO temporarily):
   ```bash
   # In /addon_configs/ee660d3e_numa/numa.toml, temporarily add to [server]:
   # (Numa uses RUST_LOG env var, set in s6 run script)
   ```
   Or check the s6 run script and set `RUST_LOG=info` temporarily.

2. **Check for stale forwarding rules** from a previous Numa run:
   ```bash
   curl -s http://127.0.0.1:5381/stats | python3 -m json.tool
   ```
   Look for a `forwarding_rules` or `routing` field (the startup banner prints `N conditional rules` if any).

3. **Apply the pending config changes** to HA:
   - Delete or update `/addon_configs/ee660d3e_numa/numa.toml`
   - Apply: `timeout_ms = 800`, DoH-only upstreams
   - Restart the add-on
   - Recheck query log latency

4. **Verify FORWARD path disappears** after config update. All queries should show `UPSTREAM` path at <100ms.

---

## Files Modified in This Investigation

| File | Change |
|---|---|
| `numa/rootfs/etc/numa/numa.toml.default` | DoH-only upstreams, `timeout_ms = 800`, updated comments |
| `numa/rootfs/etc/nginx/templates/ingress.gtpl` | Font path rewriting via `sub_filter` for HA ingress 404 fix |
| `docs/latency-investigation.md` | This document |