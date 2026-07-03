#!/usr/bin/env python3
"""discord-pfp: fetch and download Discord profile pictures and banners.

Clone of pfpfinder.com/tools/discord-pfp-downloader as a CLI.

Given a Discord user ID, resolves the user's avatar (and banner, if set)
via the public japi.rest lookup API (no auth needed), with a fallback to
the official Discord API when DISCORD_BOT_TOKEN is set. Prints metadata
(username, account creation date/age) and CDN URLs for all sizes, and can
download the images.

Stdlib only. Python 3.8+.

Usage:
  discord_pfp.py <user_id> [--size 4096] [--download] [--out DIR]
                 [--banner] [--json] [--url-only]
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

CDN = "https://cdn.discordapp.com"
SIZES = (256, 512, 1024, 4096)
DISCORD_EPOCH_MS = 1420070400000  # 2015-01-01T00:00:00Z
UA = "discord-pfp/1.0 (+https://github.com/KitsuneTech1/discord-pfp)"


def http_get(url, headers=None, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def parse_user_id(raw):
    """Accept a bare ID, a mention like <@123>, or a discord.com profile URL."""
    m = re.search(r"(\d{15,21})", raw)
    if not m:
        raise ValueError(f"no Discord user ID found in {raw!r}")
    return m.group(1)


def snowflake_created(user_id):
    ms = (int(user_id) >> 22) + DISCORD_EPOCH_MS
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)


def lookup_japi(user_id):
    data = json.loads(http_get(f"https://japi.rest/discord/v1/user/{user_id}"))
    d = data.get("data")
    if not d or "id" not in d:
        raise LookupError(f"japi.rest returned no user for {user_id}")
    return {
        "id": d["id"],
        "username": d.get("username"),
        "global_name": d.get("global_name"),
        "avatar": d.get("avatar"),
        "banner": d.get("banner"),
        "accent_color": d.get("accent_color"),
    }


def lookup_discord_api(user_id, token):
    d = json.loads(http_get(
        f"https://discord.com/api/v10/users/{user_id}",
        headers={"Authorization": f"Bot {token}"},
    ))
    return {
        "id": d["id"],
        "username": d.get("username"),
        "global_name": d.get("global_name"),
        "avatar": d.get("avatar"),
        "banner": d.get("banner"),
        "accent_color": d.get("accent_color"),
    }


def lookup(user_id):
    errors = []
    try:
        return lookup_japi(user_id)
    except Exception as e:  # noqa: BLE001 - fall through to next resolver
        errors.append(f"japi.rest: {e}")
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if token:
        try:
            return lookup_discord_api(user_id, token)
        except Exception as e:  # noqa: BLE001
            errors.append(f"discord api: {e}")
    raise LookupError("all resolvers failed: " + "; ".join(errors))


def image_urls(kind, user_id, img_hash, size):
    """kind is 'avatars' or 'banners'. Animated hashes start with 'a_'."""
    ext = "gif" if img_hash.startswith("a_") else "png"
    base = f"{CDN}/{kind}/{user_id}/{img_hash}"
    return {
        "url": f"{base}.{ext}?size={size}",
        "ext": ext,
        "animated": img_hash.startswith("a_"),
        "sizes": {s: f"{base}.{ext}?size={s}" for s in SIZES},
    }


def default_avatar_url(user_id):
    return f"{CDN}/embed/avatars/{(int(user_id) >> 22) % 6}.png"


def build_result(user, size):
    created = snowflake_created(user["id"])
    age_days = (datetime.now(timezone.utc) - created).days
    result = {
        "id": user["id"],
        "username": user.get("username"),
        "display_name": user.get("global_name") or user.get("username"),
        "created_at": created.isoformat(),
        "account_age_days": age_days,
        "avatar": None,
        "banner": None,
    }
    if user.get("avatar"):
        result["avatar"] = image_urls("avatars", user["id"], user["avatar"], size)
    else:
        result["avatar"] = {
            "url": default_avatar_url(user["id"]),
            "ext": "png",
            "animated": False,
            "default": True,
            "sizes": {},
        }
    if user.get("banner"):
        result["banner"] = image_urls("banners", user["id"], user["banner"], size)
    return result


def download(url, path):
    data = http_get(url)
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Download Discord profile pictures and banners by user ID.")
    ap.add_argument("user", help="Discord user ID (bare ID, <@mention>, or profile URL)")
    ap.add_argument("--size", type=int, default=4096, choices=SIZES, help="image size (default 4096)")
    ap.add_argument("--download", action="store_true", help="download the avatar (and banner with --banner)")
    ap.add_argument("--banner", action="store_true", help="also include/download the banner")
    ap.add_argument("--out", default=".", help="download directory (default: cwd)")
    ap.add_argument("--json", action="store_true", help="print machine-readable JSON")
    ap.add_argument("--url-only", action="store_true", help="print only the avatar URL")
    args = ap.parse_args(argv)

    try:
        user_id = parse_user_id(args.user)
        user = lookup(user_id)
        result = build_result(user, args.size)
    except Exception as e:  # noqa: BLE001
        print(f"error: {e}", file=sys.stderr)
        return 1

    if args.download:
        os.makedirs(args.out, exist_ok=True)
        targets = [("avatar", result["avatar"])]
        if args.banner and result["banner"]:
            targets.append(("banner", result["banner"]))
        result["files"] = {}
        for label, img in targets:
            name = f"{result['username'] or user_id}_{label}_{args.size}.{img['ext']}"
            name = re.sub(r"[^\w.\-]", "_", name)
            path = os.path.join(args.out, name)
            n = download(img["url"], path)
            result["files"][label] = {"path": os.path.abspath(path), "bytes": n}

    if args.url_only:
        print(result["avatar"]["url"])
        return 0
    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    print(f"user:        {result['display_name']} (@{result['username']}, {result['id']})")
    print(f"created:     {result['created_at']}  ({result['account_age_days']} days old)")
    av = result["avatar"]
    tag = " (animated)" if av.get("animated") else (" (default avatar)" if av.get("default") else "")
    print(f"avatar:      {av['url']}{tag}")
    if result["banner"]:
        print(f"banner:      {result['banner']['url']}")
    elif args.banner:
        print("banner:      none set")
    for label, info in result.get("files", {}).items():
        print(f"saved {label}: {info['path']} ({info['bytes']:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
