# AGENTS.md

Scope: applies to the whole repository.

## Project

Home Assistant add-on repository for upstream `razvandimescu/numa`.

- Add-on lives in `numa/`.
- Container uses `ghcr.io/hassio-addons/base` + downloaded upstream Numa binary.
- Runtime is s6-overlay: `init-numa`, `init-nginx`, `numa`, `nginx`.
- `host_network: true` is intentional so DNS can bind host port `53`.
- Numa API/dashboard stays loopback-only on `127.0.0.1:5381`; nginx exposes it through HA Ingress.
- DNS: `53/udp,tcp`; DoT: `853/tcp`; mobile API: `8765/tcp`.

## Do not break these invariants

- Do **not** expose Numa's unauthenticated main API on LAN. Keep `api_bind_addr = "127.0.0.1"`.
- Do **not** add HA Supervisor HTTP `watchdog`; host networking makes it probe the wrong address.
- Keep default behavior safe: `rebind_protect: false`, `.numa` proxy loopback-only unless explicitly configured.
- `/config` is backed up persistent config. `/data/numa` is for TLS/internal regenerable state and is backup-excluded.
- Upstream runtime JSON must persist under `/config/.config/numa/`; `numa/run` sets `HOME=/config` for this.
- Update `numa/apparmor.txt` whenever adding runtime paths/capabilities.
- Do not bump `numa/config.yaml` version unless explicitly requested; release/version bumps may be handled by automation.
- Never push, create branches, or modify git remotes unless explicitly requested.

## Config workflow

When adding/changing an add-on option, update all relevant places:

1. `numa/config.yaml` `options`
2. `numa/config.yaml` `schema`
3. `numa/rootfs/etc/s6-overlay/scripts/init-numa` TOML generation
4. `numa/DOCS.md` and, if user-facing, `numa/README.md` / root `README.md`
5. `numa/CHANGELOG.md` under the existing target release unless asked to cut a new one

## Upstream Numa release review

For each upstream release, compare at least:

- GitHub release notes
- upstream `numa.toml`
- upstream `src/config.rs`
- upstream runtime/persistence code when relevant (`serve.rs`, stores, API handlers)

Look specifically for new config keys, changed defaults, new persisted files, ports, auth/security changes, and dashboard/API behavior.

## Validation

Run the narrowest useful checks available:

```sh
python3 -c 'import yaml, json, pathlib; yaml.safe_load(pathlib.Path("numa/config.yaml").read_text()); yaml.safe_load(pathlib.Path("repository.yaml").read_text()); json.loads(pathlib.Path("repository.json").read_text())'
bash -n numa/rootfs/etc/s6-overlay/scripts/init-numa numa/rootfs/etc/s6-overlay/s6-rc.d/numa/run
git --no-pager diff --check
```

If available, also run `yamllint .` and markdown linting.