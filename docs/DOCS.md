# Technical Reference

## Architecture

`discord_pfp.py` is a single-file, stdlib-only Python script. It has no external dependencies and no package structure. The entry point is the `if __name__ == "__main__"` block at the bottom of the file.

Key internal components:

- **Snowflake decoding**: `snowflake_to_datetime()` extracts the Unix timestamp from a Discord snowflake ID using bitwise operations. This runs locally with no network call.
- **japi.rest resolver**: `resolve_via_japi()` calls the public `https://japi.rest/discord/v1/users/{id}` endpoint. No authentication required.
- **Discord API resolver**: `resolve_via_discord_api()` calls `GET /users/{id}` against `https://discord.com/api/v10` using a bot token from the `DISCORD_BOT_TOKEN` environment variable.
- **CDN URL construction**: `build_avatar_url()` and `build_banner_url()` construct Discord CDN URLs from the resolved hash, choosing `.gif` for animated hashes (prefixed `a_`) and `.png` otherwise.
- **Download logic**: `download_image()` writes the image bytes to disk, naming files by user ID and image type.
- **Output formatting**: `format_output()` produces the human-readable terminal output. `format_json_output()` produces a JSON object with all resolved fields and file paths.

## CLI

```
python discord_pfp.py <user> [--size {256,512,1024,4096}] [--download] [--banner] [--out DIR] [--json] [--url-only]
```

### Arguments

| Argument | Required | Description |
|---|---|---|
| `<user>` | Yes | Discord user ID (string of digits), `<@mention>` (e.g. `<@80351110224678912>`), or full `discord.com/users/...` profile URL |

### Options

| Flag | Type | Default | Description |
|---|---|---|---|
| `--size` | Choice: 256, 512, 1024, 4096 | 4096 | Requested image dimension |
| `--download` | Flag | false | Write avatar (and banner with `--banner`) to disk |
| `--banner` | Flag | false | Also resolve and optionally download the user's banner |
| `--out` | Path | `.` | Directory for downloaded files |
| `--json` | Flag | false | Output a JSON object instead of human-readable text |
| `--url-only` | Flag | false | Print only the avatar CDN URL |

### Output

**Default (human-readable):**

```
user:        username (@displayname, id)
created:     ISO 8601 timestamp  (N days old)
avatar:      CDN URL
banner:      CDN URL or "none set"
```

**JSON (`--json`):**

```json
{
  "id": "80351110224678912",
  "username": "b1nzy",
  "display_name": "b1nzy.",
  "created_at": "2015-08-10T17:26:37.529000+00:00",
  "age_days": 3979,
  "avatar_url": "https://cdn.discordapp.com/avatars/.../....png?size=4096",
  "avatar_urls": {
    "256": "...",
    "512": "...",
    "1024": "...",
    "4096": "..."
  },
  "banner_url": null,
  "banner_urls": null,
  "downloaded_avatar": null,
  "downloaded_banner": null
}
```

## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `DISCORD_BOT_TOKEN` | No | None | Discord bot token. When set, the script uses the official Discord API as a fallback if the japi.rest lookup fails. Without it, only japi.rest is attempted. |

## Data Model

No persistent storage. The script resolves user data on each invocation and discards it. Downloaded images are written to the filesystem under the directory specified by `--out` (defaults to the current working directory).

File naming convention: `{user_id}_avatar.{ext}` and `{user_id}_banner.{ext}`, where `ext` is `png` for static images and `gif` for animated ones.

## Deploy

This is a single Python file. Deployment means putting `discord_pfp.py` on a machine with Python 3.8+ and running it. No build step, no virtual environment required, no package installation.

For convenience, the project registers itself as a Claude Code user-level skill at `~/.claude/skills/discord-pfp/SKILL.md` so agent sessions can invoke it directly.

## Gotchas

- **japi.rest is a free third-party service.** It can rate-limit, throttle, or go down without notice. For reliable lookups, set `DISCORD_BOT_TOKEN`.
- **The Discord API fallback requires a bot token.** A user account token will not work. Create a bot application in the Discord Developer Portal and use its token.
- **Animated images are detected by hash prefix.** If a user has an animated avatar, the hash starts with `a_` and the script requests `.gif`. Static avatars use `.png`. Discord may serve WebP to browsers, but the CDN returns the requested format when you ask for `.png` or `.gif` explicitly.
- **Default avatars have no hash.** Users who have never set a custom avatar will resolve to Discord's default embed avatar URL, which is constructed from the user's discriminator or the new username system's modulo-based default.
- **Snowflake decoding assumes Discord epoch.** The script uses the standard Discord epoch of January 1, 2015 (1420070400000ms). This is correct for all Discord snowflakes.