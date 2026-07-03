# discord-pfp

CLI clone of [pfpfinder.com's Discord PFP Downloader](https://pfpfinder.com/tools/discord-pfp-downloader): resolve any Discord user ID to their profile picture, banner, and account-creation info, and download the images at up to 4096px.

Stdlib-only Python 3.8+, no dependencies, no auth required. Uses the public japi.rest lookup API, with an optional fallback to the official Discord API when `DISCORD_BOT_TOKEN` is set.

## Usage

```
python discord_pfp.py <user> [--size {256,512,1024,4096}] [--download] [--banner] [--out DIR] [--json] [--url-only]
```

`<user>` can be a bare user ID, a `<@mention>`, or a discord.com profile URL (the ID is extracted).

```
$ python discord_pfp.py 80351110224678912 --banner
user:        b1nzy (@b1nzy., 80351110224678912)
created:     2015-08-10T17:26:37.529000+00:00  (3979 days old)
avatar:      https://cdn.discordapp.com/avatars/.../....png?size=4096
banner:      none set
```

- `--json` gives machine-readable output including per-size CDN URLs (256/512/1024/4096) and saved file paths.
- Animated avatars/banners (hash prefixed `a_`) are returned as `.gif`, static as `.png`.
- Users with no custom avatar resolve to Discord's default embed avatar.

## Agent integration

Registered as the Claude Code user-level skill `discord-pfp` (`~/.claude/skills/discord-pfp/SKILL.md`), so every agent session on this machine knows how to call it.
