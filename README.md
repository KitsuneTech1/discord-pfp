# discord-pfp

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Dependencies: none](https://img.shields.io/badge/dependencies-none-brightgreen.svg)](discord_pfp.py)

CLI clone of [pfpfinder.com's Discord PFP Downloader](https://pfpfinder.com/tools/discord-pfp-downloader): resolve any Discord user ID to their profile picture, banner, and account-creation info, and download the images at up to 4096px.

Stdlib-only Python 3.8+, no dependencies, no auth required.

```
$ python discord_pfp.py 80351110224678912 --banner
user:        b1nzy (@b1nzy., 80351110224678912)
created:     2015-08-10T17:26:37.529000+00:00  (3979 days old)
avatar:      https://cdn.discordapp.com/avatars/.../....png?size=4096
banner:      none set
```

## Run it yourself

### What you need

- **Python 3.8 or newer.** That's it, nothing else to install. Check with `python --version` in a terminal (on Mac/Linux it may be `python3 --version` instead). It should print `Python 3.8.0` or higher. If the command errors, install from https://www.python.org/downloads/. On Windows, check the box "Add python.exe to PATH" during install, that box is easy to miss and causes most problems below.

### Step by step

1. **Open a terminal.**
   - Windows: press the Start key, type `PowerShell`, and open "Windows PowerShell".
   - Mac: open Spotlight (Cmd+Space), type `Terminal`, and open it.

2. **Get the code.** Pick one:
   - No `git` installed: on the [GitHub page](https://github.com/KitsuneTech1/discord-pfp), click the green "Code" button, choose "Download ZIP", then extract the ZIP somewhere easy to find, like your Desktop.
   - With `git` installed:
     ```bash
     git clone https://github.com/KitsuneTech1/discord-pfp.git
     ```

3. **Move into the project folder.**
   ```bash
   cd discord-pfp
   ```
   (If you downloaded the ZIP to your Desktop instead, use `cd Desktop/discord-pfp` or wherever you extracted it.)

4. **Run it.** There's no install step, no dependencies to download, this is a single Python file.
   ```bash
   python discord_pfp.py 80351110224678912 --banner
   ```
   (Use `python3` instead of `python` if that's what `python --version` needed above.) Swap in any Discord user ID you want to look up.

**It worked if:** you see lines starting with `user:`, `created:`, and `avatar:` printed in the terminal, like the example at the top of this file.

**Troubleshooting:**

- **`'python' is not recognized` / `python: command not found`.** Try `python3` instead. If neither works, Python wasn't added to PATH during install, reinstall from python.org and make sure the PATH checkbox is checked, then reopen your terminal.
- **`error: no Discord user ID found in '...'`.** The value you passed isn't a valid ID, mention, or profile URL. Copy the plain numeric ID (Discord: enable Developer Mode in Settings > Advanced, then right-click a user and "Copy User ID").
- **`error: all resolvers failed: japi.rest: ...`.** The free lookup service is temporarily down or rate-limiting you. Wait a minute and try again, or set a `DISCORD_BOT_TOKEN` environment variable with a real Discord bot token to fall back to the official API (see "How it works" below).
- **SSL certificate error on Mac.** A common first-run Mac/Python issue unrelated to this script. Run the "Install Certificates.command" file that came with your Python installation (usually in `/Applications/Python 3.x/`).

## Usage

```
python discord_pfp.py <user> [--size {256,512,1024,4096}] [--download] [--banner] [--out DIR] [--json] [--url-only]
```

`<user>` can be a bare user ID, a `<@mention>`, or a discord.com profile URL (the ID is extracted).

## Options

| Flag | Description |
|---|---|
| `<user>` | Discord user ID, `<@mention>`, or profile URL (required) |
| `--size {256,512,1024,4096}` | Image size to request (default 4096) |
| `--download` | Download the avatar (and banner with `--banner`) to disk |
| `--banner` | Also include/download the banner |
| `--out DIR` | Download directory (default: current directory) |
| `--json` | Print machine-readable JSON, including per-size CDN URLs and saved file paths |
| `--url-only` | Print only the avatar URL |

Animated avatars/banners (hash prefixed `a_`) are returned as `.gif`, static as `.png`. Users with no custom avatar resolve to Discord's default embed avatar.

## How it works

Lookups go through the public [japi.rest](https://japi.rest) Discord user endpoint, which needs no authentication. If that fails, and `DISCORD_BOT_TOKEN` is set in the environment, the script falls back to the official Discord API (`GET /users/{id}`) using that bot token.

Account creation date and age come from decoding the Discord snowflake ID directly, no API call needed for that part.

## Notes on rate limits

japi.rest is a free public service and can rate-limit or throttle under heavy use. For scripted or high-volume lookups, set `DISCORD_BOT_TOKEN` (a real Discord bot token) so the script falls back to the official API, which has its own, more predictable rate limits.

## Agent integration

Registered as the Claude Code user-level skill `discord-pfp` (`~/.claude/skills/discord-pfp/SKILL.md`), so every agent session on this machine knows how to call it.

## License

MIT, see [LICENSE](LICENSE).

---

Built by [Kitsune Technologies](https://kitsunetechnologies.org). See more of our work at [kitsunetechnologies.org/work](https://kitsunetechnologies.org/work). Issues and PRs welcome.
