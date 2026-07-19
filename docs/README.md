# discord-pfp

A single-file Python CLI that resolves any Discord user ID to their profile picture, banner, and account-creation info, and downloads the images at up to 4096px.

This project exists because pfpfinder.com's web tool is handy, but there was no offline, scriptable, dependency-free equivalent. It started as a quick clone and grew into a small utility that also decodes snowflake timestamps and falls back to the official Discord API when the free lookup service is down.

## Features

- Resolve a Discord user by raw ID, `<@mention>`, or `discord.com` profile URL
- Fetch avatar and optional banner at 256, 512, 1024, or 4096 pixels
- Download images to disk with automatic `.gif` / `.png` extension detection
- Decode account creation date and age directly from the snowflake ID (no API call)
- JSON output mode for scripting and machine consumption
- URL-only mode for piping into other tools
- Zero dependencies: stdlib-only Python 3.8+
- Optional fallback to the official Discord API when `DISCORD_BOT_TOKEN` is set

## Quickstart

You need Python 3.8 or newer. Check with `python --version` (or `python3 --version` on macOS/Linux).

```bash
# Clone the repo
git clone https://github.com/KitsuneTech1/discord-pfp.git
cd discord-pfp

# Run it (no install step, no dependencies)
python discord_pfp.py 80351110224678912 --banner
```

Swap `80351110224678912` for any Discord user ID. To get a user ID, enable Developer Mode in Discord (Settings > Advanced), right-click a user, and choose "Copy User ID".

If `python` is not found, try `python3`. If neither works, reinstall Python from python.org and check the "Add python.exe to PATH" box during installation.

## Usage

```
python discord_pfp.py <user> [--size {256,512,1024,4096}] [--download] [--banner] [--out DIR] [--json] [--url-only]
```

| Flag | Description |
|---|---|
| `<user>` | Discord user ID, `<@mention>`, or profile URL (required) |
| `--size {256,512,1024,4096}` | Image size to request (default 4096) |
| `--download` | Download the avatar (and banner with `--banner`) to disk |
| `--banner` | Also include/download the banner |
| `--out DIR` | Download directory (default: current directory) |
| `--json` | Print machine-readable JSON with per-size CDN URLs and saved file paths |
| `--url-only` | Print only the avatar URL |

## Configuration

| Environment variable | Required | Description |
|---|---|---|
| `DISCORD_BOT_TOKEN` | No | A Discord bot token used as a fallback when the primary lookup service (japi.rest) is unavailable or rate-limited. Without it, the script only uses the free public endpoint. |

## License

MIT, see [LICENSE](LICENSE).