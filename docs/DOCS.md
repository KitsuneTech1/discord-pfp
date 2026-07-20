# Technical Reference

## Architecture

The entire tool is a single file: `discord_pfp.py`. It has no external dependencies and runs on Python 3.8+.

Lookup flow:

1. Parse the user argument into a numeric Discord user ID (bare ID, `<@mention>`, or profile URL).
2. Decode the snowflake ID locally to get the account creation timestamp.
3. Call the public japi.rest Discord user endpoint to fetch avatar and banner hashes.
4. If japi.rest fails and `DISCORD_BOT_TOKEN` is set in the environment, fall back to the official Discord API (`GET /users/{id}`).
5. Construct CDN URLs from the hashes at the requested size.
6. Optionally download the images and/or print JSON.

## CLI

```
python discord_pfp.py <user> [--size {256,512,1024,4096}] [--download] [--banner] [--out DIR] [--json] [--url-only]
```

### Arguments

| Argument | Required | Description |
|---|---|---|
| `<user>` | Yes | Discord user ID, `<@mention>`, or `discord.com` profile URL |
| `--size` | No | Image size to request from CDN (default: 4096) |
| `--download` | No | Download avatar (and banner when `--banner` is set) to disk |
| `--banner` | No | Also fetch and optionally download the user's banner |
| `--out` | No | Directory for downloaded files (default: current directory) |
| `--json` | No | Print machine-readable JSON with per-size CDN URLs and saved file paths |
| `--url-only` | No | Print only the avatar URL and exit |

### Output

Default output is human-readable text:

```
user:        username (@displayname, id)
created:     ISO timestamp  (N days old)
avatar:      CDN URL
banner:      CDN URL or "none set"
```

With `--json`, a single JSON object is printed to stdout containing user metadata, CDN URLs at all sizes, and local file paths when `--download` is used.

With `--url-only`, only the avatar URL string is printed.

## Configuration

| Variable | Required | Description |
|---|---|---|
| `DISCORD_BOT_TOKEN` | No | Discord bot token used as a fallback when the japi.rest public endpoint is unavailable. The script calls `GET /users/{id}` on the Discord API with this token. Without it, only the public endpoint is tried. |

## Data model

No persistent storage. The script fetches data per invocation and exits. Downloaded files are written to the directory specified by `--out` (or the current working directory) with names derived from the user ID and image type.

## Deploy

No build or install step. Copy `discord_pfp.py` to any machine with Python 3.8+. Run it directly.

For agent integration, the project registers as a Claude Code user-level skill at `~/.claude/skills/discord-pfp/SKILL.md`.

## Gotchas

- japi.rest is a free public service with no uptime guarantee. It can rate-limit or throttle under heavy use. For scripted or high-volume lookups, set `DISCORD_BOT_TOKEN` so the script falls back to the official API.
- Users without a custom avatar resolve to Discord's default embed avatar. The CDN URL reflects this.
- Animated avatars and banners have a hash prefixed with `a_`. The script detects this and saves them as `.gif` instead of `.png`.
- The account creation date is decoded from the snowflake ID locally. It does not depend on any API call and is always available.