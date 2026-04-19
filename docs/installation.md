# Numa — Installation Guide

## Prerequisites

Before installing Numa on Home Assistant OS, make sure:

1. **Your Home Assistant device has a static IP address.**
   This is critical. If your HA device uses DHCP, changing its DNS server to itself will cause a boot loop if the IP ever changes.

   Configure a static IP in:
   _Settings → System → Network → Configure network interfaces → Your Interface → IPv4 → Static_

2. **Set static external DNS servers** (e.g. `9.9.9.9`, `1.1.1.1`) on the same network interface.
   This ensures Home Assistant can still resolve hostnames during Numa startup.

---

## Adding the custom repository

1. In Home Assistant, go to **Settings → Add-ons → Add-on Store**.
2. Click the **⋮ (three-dot menu)** in the top-right corner.
3. Select **Repositories**.
4. Add the following URL:
   ```
   https://github.com/Guara92/numa-haos
   ```
5. Click **Add**, then close the dialog.
6. The **Numa** app should now appear in the store. If it does not, refresh the page.

---

## Installing Numa

1. Click on **Numa** in the Add-on Store.
2. Click **Install** and wait for the image to be pulled and built.
3. After installation, go to the **Configuration** tab to review the default options.
4. Click **Start**.
5. Open the **Log** tab and verify that Numa started without errors.

---

## Accessing the dashboard

Once the app is running, you have two ways to access the Numa dashboard:

- Click **Open Web UI** from the app page.
- Use the **Numa** entry in the Home Assistant sidebar (if panel is enabled).

---

## First-run configuration

On first boot, Numa will write a default `numa.toml` to the persistent config directory:

```
/addon_configs/<slug>/numa.toml
```

You can edit this file:
- via the **File Editor** or **SSH & Terminal** add-ons, or
- via the built-in minimal TOML editor served through Ingress (Phase 4, coming soon).

After editing `numa.toml`, restart the Numa add-on for changes to take effect.

---

## DNS configuration on your network

To use Numa as your network-wide DNS resolver, point your router's DNS server to the static IP of your Home Assistant device.

> **Important:** Do this *after* confirming Numa is running correctly. If Numa is not running and your router points DNS to it, all network name resolution will fail.

---

## Updating Numa

When a new version is released:

1. Go to the Numa add-on page in Home Assistant.
2. Click **Update**.
3. Your `numa.toml` configuration is preserved across updates.

---

## Uninstalling

1. Go to the Numa add-on page.
2. Click **Uninstall**.
3. Your `numa.toml` config file in `/addon_configs/<slug>/` is **not** automatically deleted and can be backed up or reused.