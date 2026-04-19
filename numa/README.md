# Home Assistant App: Numa

[![GitHub Release][releases-shield]][releases]
![Project Stage][project-stage-shield]
[![License][license-shield]](../LICENSE)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]

[![GitHub Activity][commits-shield]][commits]

Self-hosted DNS resolver with ad blocking, local proxy, and dashboard — designed for your home network.

## About

[Numa][numa] is a self-contained DNS resolver that combines:

- **Ad blocking** via DNS-based blocklists
- **Local proxy** with `.numa` TLD for your home services
- **DNS-over-HTTPS / DNS-over-TLS** support
- **Conditional forwarding** per domain suffix
- **A clean dashboard** accessible from your browser

This Home Assistant App lets you install and run Numa on Home Assistant OS or
Supervised, with the dashboard accessible directly from the Home Assistant sidebar
via native Ingress.

## Installation

1. Add this repository to your Home Assistant instance:

   [![Add Repository][repo-badge]][repo-url]

   Or manually add the following URL in
   _Settings → Add-ons → Add-on Store → (three dots) → Repositories_:

   ```text
   https://github.com/Guara92/numa-haos
   ```

2. Find **Numa** in the App Store and click **Install**.
3. Start the app.
4. Check the logs to confirm Numa started correctly.
5. Click **Open Web UI** or the sidebar entry to open the Numa dashboard.

> **Important:** For Numa to handle DNS on your network, your Home Assistant
> device needs a **static IP address**. Set this in
> _Settings → System → Network_.

## Documentation

Full documentation is available in [DOCS.md][docs].

## Configuration

The app exposes a minimal set of options. Numa's full configuration is managed
via `numa.toml`, stored at `/addon_configs/numa/numa.toml` on your Home
Assistant host.

On first start, a default `numa.toml` is written automatically if none exists.

See [DOCS.md][docs] for details on all configuration options.

## Support

- Open an [issue on GitHub][issue]
- Visit the [Numa project][numa]

## License

MIT License

Copyright (c) 2024 Guara92

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[commits-shield]: https://img.shields.io/github/commit-activity/y/Guara92/numa-haos.svg
[commits]: https://github.com/Guara92/numa-haos/commits/main
[docs]: https://github.com/Guara92/numa-haos/blob/main/numa/DOCS.md
[issue]: https://github.com/Guara92/numa-haos/issues
[license-shield]: https://img.shields.io/github/license/Guara92/numa-haos.svg

[numa]: https://github.com/razvandimescu/numa
[project-stage-shield]: https://img.shields.io/badge/project%20stage-experimental-yellow.svg
[releases-shield]: https://img.shields.io/github/release/Guara92/numa-haos.svg
[releases]: https://github.com/Guara92/numa-haos/releases
[repo-badge]: https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg
[repo-url]: https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FGuara92%2Fnuma-haos
