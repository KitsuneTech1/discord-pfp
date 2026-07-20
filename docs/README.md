# discord-pfp

CLI tool to resolve a Discord user ID to profile picture, banner, and account-creation info, and download the images at up to 4096px.

This project exists because the web-based pfpfinder.com downloader is convenient but not scriptable. A single-file, zero-dependency Python script fills that gap for automation, bots, and headless environments.

## Features

- Resolve any Discord user by ID, mention, or profile URL
- Fetch avatar and optional banner at 256, 512, 1024, or 4096 pixels
- Download images to disk with automatic file naming
- Output machine-readable JSON with per-size CDN URLs and saved file paths
- Decode account creation date directly from the snowflake ID, no API call needed
- Fall back to the official Discord API when a bot token is provided
- Animated avatars and banners are saved as `.gif`, static as `.png`

## Quickstart

You need Python 3.8 or newer. Nothing else to install.

```bash
git clone https://github.com/KitsuneTech1/discord-pfp.git
cd discord-pfp
python discord_pfp.py 80351110224678912 --banner
```

Swap `80351110224678912` for any Discord user ID. Use `python3` if your system requires it.

## Configuration

| Variable | Required | Description |
|---|---|---|
| `DISCORD_BOT_TOKEN` | No | Discord bot token for official API fallback when the public lookup service is unavailable or rate-limited |

## License

MIT, see [LICENSE](LICENSE).