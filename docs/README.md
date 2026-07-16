# discord-pfp

A single-file Python CLI that resolves any Discord user ID to their profile picture, banner, and account-creation info, and downloads the images at up to 4096px.

This project exists because the web-based pfpfinder.com tool is convenient but not scriptable. A zero-dependency CLI lets you batch lookups, pipe output into other tools, and run it anywhere Python 3.8+ is available.

## Features

- Resolve a Discord user by raw ID, `<@mention>`, or profile URL
- Fetch avatar and optional banner at sizes 256, 512, 1024, or 4096
- Download images to disk with automatic `.png` or `.gif` extension
- Print machine-readable JSON output for scripting
- Decode account creation date directly from the snowflake ID, no API call needed
- Falls back to the official Discord API when a bot token is provided

## Quickstart

```bash
git clone https://github.com/KitsuneTech1/discord-pfp.git
cd discord-pfp
python discord_pfp.py 80351110224678912 --banner
```

Use `python3` if your system requires it. No install step, no dependencies.

## Configuration

| Variable | Required | Purpose |
|---|---|---|
| `DISCORD_BOT_TOKEN` | No | Discord bot token for official API fallback when japi.rest is unavailable or rate-limited |

## License

MIT, see [LICENSE](LICENSE).