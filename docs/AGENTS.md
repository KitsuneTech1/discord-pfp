# Agent Guide

## Orientation

This is a single-file Python CLI (`discord_pfp.py`) that looks up Discord user profile information. It takes a user identifier (ID, mention, or profile URL), resolves the avatar and optionally the banner, and can download the images. No dependencies, no install step, no auth required for basic use.

## How to Run

```bash
# Basic lookup
python discord_pfp.py 80351110224678912

# With banner
python discord_pfp.py 80351110224678912 --banner

# Download avatar at 1024px
python discord_pfp.py 80351110224678912 --size 1024 --download

# JSON output for parsing
python discord_pfp.py 80351110224678912 --json

# URL only, useful for piping
python discord_pfp.py 80351110224678912 --url-only
```

Use `python3` if the system requires it.

## How to Test

```bash
# Smoke test: a well-known user ID should return data
python discord_pfp.py 80351110224678912 --json

# Verify the JSON output contains expected keys
python discord_pfp.py 80351110224678912 --json | python -c "import sys,json; d=json.load(sys.stdin); assert 'avatar_url' in d; print('OK')"

# Test with a mention format
python discord_pfp.py '<@80351110224678912>' --url-only

# Test download creates a file
python discord_pfp.py 80351110224678912 --download --out /tmp
ls /tmp/80351110224678912_avatar.*
```

## What an Agent Must Know

1. **This is a single file with no dependencies.** Do not run `pip install`, do not create a virtual environment, do not look for `setup.py` or `pyproject.toml`. Just run `python discord_pfp.py`.

2. **The primary lookup service is japi.rest, a free third-party API.** It requires no authentication but can be flaky. If lookups fail with "all resolvers failed," the agent should either wait and retry, or advise the user to set `DISCORD_BOT_TOKEN` in their environment.

3. **`DISCORD_BOT_TOKEN` is an optional env var for fallback.** It must be a Discord bot token (not a user token). The agent should never hardcode, commit, or log this value. If the user provides it, set it inline:
   ```bash
   DISCORD_BOT_TOKEN=... python discord_pfp.py 80351110224678912
   ```

4. **The script writes files to disk when `--download` is passed.** Files land in the current working directory unless `--out` specifies another path. The agent should be aware of the working directory and clean up test files if needed.

5. **User identifiers accept three formats:** raw numeric ID, `<@mention>` (with angle brackets and optional exclamation mark), and `discord.com/users/...` URLs. The script extracts the ID internally. The agent can pass any of these formats directly.

6. **Exit codes:** The script exits 0 on success and non-zero on failure. The agent can check `$?` after a run to determine if the lookup succeeded.

7. **Rate limits:** japi.rest has no documented rate limit but can throttle. The Discord API fallback has standard Discord rate limits (roughly 50 requests per second per token). The agent should not hammer either service in a tight loop without delays.

8. **The project registers itself as a Claude Code skill** at `~/.claude/skills/discord-pfp/SKILL.md`. If the agent is running in Claude Code, it can invoke the skill directly rather than shelling out, but the CLI works either way.

## Common Call Shape

There is no HTTP API or MCP server here. The only interface is the CLI. Every invocation follows this shape:

```bash
python discord_pfp.py <user_identifier> [--size N] [--download] [--banner] [--out PATH] [--json] [--url-only]
```

For scripting, prefer `--json` and parse stdout. For simple URL extraction, use `--url-only`. For human display, use the default output with no flags beyond `--banner` if needed.