# Agent guide for discord-pfp

## Orientation

This is a single-file Python CLI (`discord_pfp.py`) that looks up Discord user profile pictures, banners, and account creation dates. It has zero dependencies and targets Python 3.8+. The primary data source is the free japi.rest public endpoint, with an optional fallback to the official Discord API when `DISCORD_BOT_TOKEN` is set.

## How to run and test

### Run the tool

```bash
python discord_pfp.py <user_id> [flags]
```

On macOS/Linux, you may need `python3` instead of `python`.

### Quick smoke test

```bash
python discord_pfp.py 80351110224678912
```

Expected: prints `user:`, `created:`, and `avatar:` lines. Exit code 0.

### Test with flags

```bash
# JSON output
python discord_pfp.py 80351110224678912 --json

# URL only
python discord_pfp.py 80351110224678912 --url-only

# Download avatar and banner at 512px
python discord_pfp.py 80351110224678912 --banner --download --size 512 --out /tmp/pfp-test
```

### Test error handling

```bash
# Invalid user ID
python discord_pfp.py not-a-user-id
# Expected: error message, exit code 1

# Valid ID but japi.rest down (unset DISCORD_BOT_TOKEN to simulate)
# Expected: "all resolvers failed" error, exit code 1
```

### Run with bot token fallback

```bash
DISCORD_BOT_TOKEN="your-token-here" python discord_pfp.py 80351110224678912
```

## What an agent must know to work here safely

1. **No install step.** Do not run `pip install` or create a virtual environment. The script uses only the standard library. Just run `python discord_pfp.py`.

2. **Do not commit secrets.** `DISCORD_BOT_TOKEN` is read from the environment at runtime. Never hardcode a token in the script or write it to any file in the repo. If you need to test with a token, pass it inline in the shell or set it in your local environment.

3. **No `.env` file support.** The script does not read `.env` files. Do not create one expecting it to work. Set environment variables directly in the shell.

4. **Single file, no modules.** All logic lives in `discord_pfp.py`. There are no subpackages, no `setup.py`, no `pyproject.toml`. Do not refactor into multiple files unless explicitly asked.

5. **Python version floor is 3.8.** Do not use syntax or stdlib features added after Python 3.8 (no `str.removeprefix` without a fallback, no `match`/`case`, no `typing` features from 3.9+).

6. **japi.rest is external and flaky.** The primary lookup can fail due to rate limiting or downtime. The fallback to the official Discord API only triggers when `DISCORD_BOT_TOKEN` is set. When writing code that calls this tool, handle exit code 1 gracefully.

7. **Output formats are stable.** The human-readable format prints to stdout with specific labels (`user:`, `created:`, `avatar:`, `banner:`). The `--json` flag outputs a single JSON object. The `--url-only` flag outputs a bare URL with no trailing newline. Do not change these formats without updating any downstream consumers.

8. **Image extensions are determined by hash prefix.** Animated avatars and banners have hashes starting with `a_` and get a `.gif` extension. Static images get `.png`. This logic is in the CDN URL construction and download code. Do not second-guess it based on Content-Type headers.

9. **Snowflake decoding is local and deterministic.** The account creation date comes from bit-shifting the user ID, not from an API response. It will always match Discord's actual creation time. Do not replace this with an API call.

10. **The repo includes generated docs.** The `docs/` directory contains `README.md`, `DOCS.md`, and `AGENTS.md`. These are generated artifacts. When updating the tool, update the source code and this agent guide, then regenerate the docs rather than editing them directly.

## Common call shape (CLI)

This tool is a CLI, not an HTTP or MCP server. The call shape is always:

```bash
python discord_pfp.py <user> [--size SIZE] [--download] [--banner] [--out DIR] [--json] [--url-only]
```

- `<user>` accepts a raw ID, `<@mention>`, or `https://discord.com/users/...` URL.
- Output goes to stdout. Downloaded files go to `--out` (default: cwd).
- Exit code 0 on success, 1 on any failure.

If you are integrating this into an agent workflow, parse the stdout for the human-readable format, or use `--json` and parse the JSON object. For piping the avatar URL into another command, use `--url-only`.