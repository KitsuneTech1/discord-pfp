# Agent Guide

## Orientation

This is a single-file Python CLI (`discord_pfp.py`) that resolves Discord user IDs to profile pictures, banners, and account creation dates. It has zero dependencies and runs on Python 3.8+. It is registered as a Claude Code skill on the maintainer's machine, so agent sessions already know how to invoke it.

## How to run

```bash
python discord_pfp.py <user_id> [flags]
```

Use `python3` if the system requires it. No install step, no virtual environment needed.

## How to test

A basic smoke test is to run the script against a known Discord user ID and confirm it prints `user:`, `created:`, and `avatar:` lines without errors:

```bash
python discord_pfp.py 80351110224678912
```

For JSON output:

```bash
python discord_pfp.py 80351110224678912 --json
```

For download:

```bash
python discord_pfp.py 80351110224678912 --download --banner --out /tmp
```

There is no test suite in the repo. Manual invocation is the verification method.

## What an agent must know

- The script makes outbound HTTP requests to `japi.rest` and optionally to `discord.com/api`. It will fail on air-gapped networks unless `DISCORD_BOT_TOKEN` is set and the official API is reachable.
- `DISCORD_BOT_TOKEN` is read from the environment. Never hardcode a token in the script or commit one. The token should live in a `.env` file or the shell environment.
- The script writes files to disk only when `--download` is passed. Without it, no side effects occur.
- User IDs are 17-19 digit numbers. The script also accepts `<@mention>` format and `discord.com/users/...` profile URLs, extracting the ID from them.
- Animated avatars and banners are detected by the `a_` hash prefix and saved as `.gif`. Static images are saved as `.png`.
- The account creation date comes from the snowflake ID itself, decoded locally. It is always available even if both API endpoints are down.
- The japi.rest endpoint is a public free service. It can rate-limit. If an agent is doing bulk lookups, it should set `DISCORD_BOT_TOKEN` and expect the script to fall back to the official API automatically.

## Common call shape

The script is a CLI, not an HTTP or MCP server. Invoke it as a subprocess:

```bash
python discord_pfp.py <user> [--size N] [--download] [--banner] [--out DIR] [--json] [--url-only]
```

For machine consumption, use `--json` and parse stdout. Exit code 0 means success, non-zero means failure (with an error message on stderr).