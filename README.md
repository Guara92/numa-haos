# Numa for Home Assistant

[![License][license-shield]](LICENSE)
![Project Stage][project-stage-shield]

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]

[![GitHub Activity][commits-shield]][commits]

A Home Assistant App repository for **Numa** — a self-hosted DNS resolver with
ad blocking, local service discovery, DNS-over-HTTPS/TLS, and a built-in
reverse proxy for `.numa` domains.

## About

[Numa][numa] is a single-binary DNS server designed for home and small-office
networks. It combines recursive or forwarding DNS resolution, network-wide ad
blocking, caching, DNS-over-TLS/HTTPS, and a lightweight reverse proxy that
makes local services reachable at human-friendly `.numa` addresses.

This repository provides the Home Assistant App that lets you install and run
Numa directly from the Home Assistant Supervisor, with:

- **Sidebar access** to the Numa dashboard via Home Assistant Ingress.
- **Persistent configuration** — your `numa.toml` survives restarts and updates.
- **Minimal config workflow** — edit `numa.toml` from within Home Assistant,
  no SSH required.

## Installation

1. Navigate to **Settings → Add-ons → Add-on Store** in your Home Assistant
   instance.
2. Click the three-dot menu in the top-right corner and select
   **Repositories**.
3. Add the following repository URL:

   ```text
   https://github.com/Guara92/numa-haos
   ```

4. Find **Numa** in the store and click **Install**.
5. Start the app and open the web UI from the sidebar.

> **Note:** Make sure your Home Assistant device has a **static IP address**
> and **static external DNS servers** configured before enabling Numa as your
> network DNS. See the [networking docs](docs/networking.md) for details.

## Documentation

- [Installation guide](docs/installation.md)
- [Networking & DNS setup](docs/networking.md)
- [Architecture overview](docs/architecture.md)
- [App-level documentation](numa/DOCS.md)

## Apps in this repository

| App | Description | Version |
|-----|-------------|---------|
| [Numa](numa/) | Self-hosted DNS resolver with ad blocking and local service proxy | ![Version][numa-version-shield] |

## Contributing

Contributions are welcome. Please open an issue or pull request on GitHub.

## License

MIT License — Copyright (c) 2026 Guara92

See [LICENSE](LICENSE) for the full text.

---

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[commits-shield]: https://img.shields.io/github/commit-activity/y/Guara92/numa-haos.svg
[commits]: https://github.com/Guara92/numa-haos/commits/main
[license-shield]: https://img.shields.io/github/license/Guara92/numa-haos.svg
[numa]: https://github.com/razvandimescu/numa
[numa-version-shield]: https://img.shields.io/badge/version-0.2.0-blue.svg
[project-stage-shield]: https://img.shields.io/badge/project%20stage-experimental-yellow.svg
