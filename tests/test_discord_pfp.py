import contextlib
import io
import json
import os
import unittest
from datetime import datetime, timezone
from unittest import mock

import discord_pfp


class DiscordPfpTests(unittest.TestCase):
    def test_parse_user_id_accepts_documented_inputs_only(self):
        user_id = "80351110224678912"
        self.assertEqual(discord_pfp.parse_user_id(user_id), user_id)
        self.assertEqual(discord_pfp.parse_user_id(f"<@{user_id}>"), user_id)
        self.assertEqual(discord_pfp.parse_user_id(f"<@!{user_id}>"), user_id)
        self.assertEqual(
            discord_pfp.parse_user_id(f"https://discord.com/users/{user_id}/"), user_id
        )
        self.assertEqual(
            discord_pfp.parse_user_id(f"https://discordapp.com/users/{user_id}"), user_id
        )

        for value in ("", "not-a-user-" + user_id, f"https://example.test/{user_id}"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    discord_pfp.parse_user_id(value)

    def test_snowflake_created_matches_known_id(self):
        created = discord_pfp.snowflake_created("80351110224678912")
        self.assertEqual(created, datetime(2015, 8, 10, 17, 26, 37, 529000, tzinfo=timezone.utc))

    def test_image_urls_support_static_and_animated_assets(self):
        static = discord_pfp.image_urls("avatars", "123456789012345", "hash", 1024)
        self.assertEqual(static["url"], "https://cdn.discordapp.com/avatars/123456789012345/hash.png?size=1024")
        self.assertFalse(static["animated"])
        self.assertEqual(set(static["sizes"]), set(discord_pfp.SIZES))

        animated = discord_pfp.image_urls("banners", "123456789012345", "a_hash", 256)
        self.assertEqual(animated["ext"], "gif")
        self.assertTrue(animated["animated"])

    def test_image_urls_reject_untrusted_path_syntax(self):
        for image_hash in ("../secret", "hash?size=1", "hash#fragment", "hash/name", "hash\\name"):
            with self.subTest(image_hash=image_hash):
                with self.assertRaises(ValueError):
                    discord_pfp.image_urls("avatars", "123456789012345", image_hash, 1024)

    def test_http_get_rejects_oversized_responses(self):
        class Response:
            def __enter__(self):
                return self

            def __exit__(self, *unused):
                return False

            def read(self, size):
                return b"x" * (discord_pfp.MAX_RESPONSE_BYTES + 1)

        with mock.patch.object(discord_pfp.urllib.request, "urlopen", return_value=Response()):
            with self.assertRaisesRegex(ValueError, "exceeds"):
                discord_pfp.http_get("https://cdn.example/avatar.png")

    def test_build_result_uses_default_avatar_when_missing(self):
        result = discord_pfp.build_result(
            {"id": "80351110224678912", "username": "user", "global_name": None},
            4096,
        )
        self.assertEqual(result["display_name"], "user")
        self.assertTrue(result["avatar"]["default"])
        self.assertIsNone(result["banner"])

    def test_lookup_falls_back_to_discord_api_with_token(self):
        api_user = {"id": "123456789012345", "username": "user", "avatar": None}
        with mock.patch.object(discord_pfp, "lookup_japi", side_effect=OSError("offline")):
            with mock.patch.object(discord_pfp, "lookup_discord_api", return_value=api_user) as fallback:
                with mock.patch.dict(os.environ, {"DISCORD_BOT_TOKEN": "test-token"}):
                    self.assertEqual(discord_pfp.lookup("123456789012345"), api_user)
        fallback.assert_called_once_with("123456789012345", "test-token")

    def test_resolver_rejects_response_for_a_different_user(self):
        payload = json.dumps({"data": {"id": "123456789012346"}}).encode()
        with mock.patch.object(discord_pfp, "http_get", return_value=payload):
            with self.assertRaisesRegex(LookupError, "different Discord user"):
                discord_pfp.lookup_japi("123456789012345")

    def test_lookup_redacts_token_from_fallback_errors(self):
        token = "secret-token"
        with mock.patch.object(discord_pfp, "lookup_japi", side_effect=OSError("offline")):
            with mock.patch.object(
                discord_pfp,
                "lookup_discord_api",
                side_effect=RuntimeError(f"provider echoed {token}"),
            ):
                with mock.patch.dict(os.environ, {"DISCORD_BOT_TOKEN": token}):
                    with self.assertRaises(LookupError) as failure:
                        discord_pfp.lookup("123456789012345")
        self.assertNotIn(token, str(failure.exception))
        self.assertIn("[redacted]", str(failure.exception))

    def test_download_writes_http_bytes_without_network(self):
        destination = os.path.join("downloads", "avatar.png")
        writer = mock.mock_open()
        with mock.patch.object(discord_pfp, "http_get", return_value=b"image-bytes") as get:
            with mock.patch("builtins.open", writer):
                self.assertEqual(discord_pfp.download("https://cdn.example/avatar.png", destination), 11)
        get.assert_called_once_with("https://cdn.example/avatar.png")
        writer.assert_called_once_with(destination, "xb")
        writer().write.assert_called_once_with(b"image-bytes")

    def test_download_does_not_overwrite_existing_file(self):
        destination = os.path.join("downloads", "avatar.png")
        writer = mock.Mock(side_effect=FileExistsError(destination))
        with mock.patch.object(discord_pfp, "http_get", return_value=b"replacement"):
            with mock.patch("builtins.open", writer):
                with self.assertRaises(FileExistsError):
                    discord_pfp.download("https://cdn.example/avatar.png", destination)
        writer.assert_called_once_with(destination, "xb")

    def test_cli_download_json_path_is_network_free_when_lookup_is_stubbed(self):
        user = {
            "id": "80351110224678912",
            "username": "test-user",
            "global_name": "Test User",
            "avatar": "avatar-hash",
            "banner": "banner-hash",
        }
        output = io.StringIO()
        with mock.patch.object(discord_pfp, "lookup", return_value=user):
            with mock.patch.object(discord_pfp.os, "makedirs") as makedirs:
                with mock.patch.object(discord_pfp, "download", side_effect=[5, 5]) as download:
                    with contextlib.redirect_stdout(output):
                        status = discord_pfp.main(
                            ["80351110224678912", "--banner", "--download", "--json", "--out", "downloads"]
                        )

        self.assertEqual(status, 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["display_name"], "Test User")
        self.assertEqual(set(result["files"]), {"avatar", "banner"})
        makedirs.assert_called_once_with("downloads", exist_ok=True)
        self.assertEqual(download.call_count, 2)
        download.assert_has_calls([
            mock.call(
                "https://cdn.discordapp.com/avatars/80351110224678912/avatar-hash.png?size=4096",
                os.path.join("downloads", "test-user_avatar_4096.png"),
            ),
            mock.call(
                "https://cdn.discordapp.com/banners/80351110224678912/banner-hash.png?size=4096",
                os.path.join("downloads", "test-user_banner_4096.png"),
            ),
        ])
        self.assertTrue(result["files"]["avatar"]["path"].endswith("test-user_avatar_4096.png"))
        self.assertTrue(result["files"]["banner"]["path"].endswith("test-user_banner_4096.png"))

    def test_cli_reports_download_errors_without_traceback(self):
        user = {"id": "80351110224678912", "username": "test-user", "avatar": "avatar-hash"}
        error = io.StringIO()
        with mock.patch.object(discord_pfp, "lookup", return_value=user):
            with mock.patch.object(discord_pfp.os, "makedirs"):
                with mock.patch.object(discord_pfp, "download", side_effect=OSError("disk full")):
                    with contextlib.redirect_stderr(error):
                        status = discord_pfp.main(["80351110224678912", "--download"])
        self.assertEqual(status, 1)
        self.assertIn("error: download failed: disk full", error.getvalue())
        self.assertNotIn("Traceback", error.getvalue())

    def test_cli_rejects_conflicting_output_and_download_flags(self):
        with mock.patch.object(discord_pfp, "lookup") as lookup:
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    discord_pfp.main(["80351110224678912", "--url-only", "--download"])
        lookup.assert_not_called()

    def test_cli_rejects_unrecognized_input_before_lookup(self):
        with mock.patch.object(discord_pfp, "lookup") as lookup:
            with contextlib.redirect_stderr(io.StringIO()):
                status = discord_pfp.main(["not-a-user-80351110224678912"])
        self.assertEqual(status, 1)
        lookup.assert_not_called()


if __name__ == "__main__":
    unittest.main()
