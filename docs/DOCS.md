# discord-pfp technical reference

## Architecture

The entire tool is a single file: `discord_pfp.py`. It has no external dependencies and runs on Python 3.8 or newer using only the standard library.

### File responsibilities

- **`discord_pfp.py`** - All logic: CLI argument parsing, user ID extraction from mentions and URLs, snowflake timestamp decoding, HTTP requests to japi.rest and the Discord API, image download, and output formatting (human-readable, JSON, URL-only).

### Lookup flow

1. Parse `<user>` argument into a numeric Discord user ID (strip mentions, extract from URLs).
2. Decode the snowflake ID locally to get the account creation timestamp and age. No network call needed for this step.
3. Attempt to fetch user profile data from `https://japi.rest/discord/v1/user/{id}` (no authentication).
4. If japi.rest fails and `DISCORD_BOT_TOKEN` is set in the environment, fall back to the official Discord API `GET /users/{id}` with the bot token in the `Authorization` header.
5. Construct CDN URLs for the avatar and optional banner at the requested size.
6. If `--download` is passed, fetch the image bytes and write them to disk with the correct extension (`.gif` for animated hashes prefixed `a_`, `.png` otherwise).
7. Print output in the requested format.

## CLI reference

### Arguments

| Argument | Type | Required | Description |
|---|---|---|---|
| `user` | positional | yes | Discord user ID (numeric string), `<@mention>`, or `https://discord.com/users/...` URL. The script extracts the numeric ID from mentions and URLs. |
| `--size` | choice | no | One of `256`, `512`, `1024`, `4096`. Controls the `?size=` query parameter on CDN URLs. Default: `4096`. |
| `--download` | flag | no | When set, downloads the avatar image (and banner if `--banner` is also set) to the directory specified by `--out`. |
| `--banner` | flag | no | When set, also fetches and optionally downloads the user's banner image. Users without a banner show "none set". |
| `--out` | string | no | Directory to save downloaded images. Default: current working directory. Created if it does not exist. |
| `--json` | flag | no | Output a JSON object containing user info, per-size CDN URLs, and (if downloaded) local file paths. |
| `--url-only` | flag | no | Print only the avatar CDN URL to stdout. Mutually exclusive with `--json` in practice; the last flag wins if both are passed. |

### Output formats

**Default (human-readable):**

```
user:        username (@displayname, id)
created:     ISO 8601 timestamp  (N days old)
avatar:      CDN URL
banner:      CDN URL or "none set"
```

**`--json`:** A single JSON object with keys: `user`, `id`, `created`, `created_iso`, `age_days`, `avatar_url`, `banner_url` (or `null`), and when `--download` is used, `avatar_path` and `banner_path`.

**`--url-only`:** The avatar CDN URL as a plain string, no trailing newline.

### Exit codes

| Code | Meaning |
|---|---|
| 0 | Success |
| 1 | Error (invalid user input, all resolvers failed, network error) |

## Configuration

### Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DISCORD_BOT_TOKEN` | No | (unset) | A Discord bot token. When set, the script uses it as a fallback for the official Discord API (`GET /users/{id}`) if the primary japi.rest lookup fails. The token is sent as `Authorization: Bot {token}`. Without this variable, only japi.rest is tried. |

No `.env` file is read automatically. Set the variable in your shell or CI environment.

## Data model

There is no persistent storage. All data is fetched live and output to stdout or written as image files.

### Snowflake decoding

Discord user IDs are 64-bit snowflakes. The script extracts the timestamp by right-shifting the ID by 22 bits and adding the Discord epoch (1,420,070,400,000 milliseconds Unix). This yields the account creation time in UTC without any API call.

### CDN URL structure

- Avatar: `https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.{ext}?size={size}`
- Banner: `https://cdn.discordapp.com/banners/{user_id}/{banner_hash}.{ext}?size={size}`

Extension is `.gif` when the hash starts with `a_` (animated), otherwise `.png`. Users without a custom avatar get Discord's default embed avatar, which is a PNG with a numeric discriminator-based hash.

## Deploy

There is no build or deploy step. The script is a single Python file with no dependencies. To use it on any machine:

1. Ensure Python 3.8+ is installed.
2. Copy `discord_pfp.py` to the target machine.
3. Run it directly.

For CI or automated use, set `DISCORD_BOT_TOKEN` in the environment to avoid japi.rest rate limits.

## Gotchas

- **japi.rest rate limits:** The free public endpoint can throttle or go down. For scripted or high-volume use, set `DISCORD_BOT_TOKEN` so the official API fallback kicks in.
- **Bot token permissions:** The bot token only needs the `Gateway Intent` privileges that come with any bot account. No special scopes are required because the script only calls `GET /users/{id}`, which is available to all bot tokens.
- **Default avatars:** Users who have never set a custom avatar resolve to Discord's default embed avatar. The hash for these is derived from the user's discriminator modulo 5, not from a stored avatar hash.
- **Banner availability:** Many users do not have a banner set. The script prints "none set" and sets `banner_url` to `null` in JSON output.
- **Animated vs static:** The script checks the `a_` prefix on the hash to decide the file extension. This is reliable per Discord's CDN conventions.
- **SSL certificates on macOS:** Some macOS Python installations have incomplete certificate bundles. If you see SSL errors, run the `Install Certificates.command` script that ships with the Python installer (usually in `/Applications/Python 3.x/`).
- **No `.env` support:** The script reads `DISCORD_BOT_TOKEN` from the environment only. It does not parse `.env` files.