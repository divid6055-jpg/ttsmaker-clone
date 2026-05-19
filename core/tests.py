"""
Tests for the TTSMaker Clone API.

Real TTS engine calls (edge-tts / gTTS) are mocked so the suite stays fast,
deterministic, and offline-safe. A separate ``EngineSmokeTest`` block can be
enabled with EDGE_TTS_LIVE=1 to verify against the live service.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from unittest import mock

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from core import voices as voices_module
from core.tts_engine import SynthesisResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _fake_synthesize(*, text, voice_id, audio_format, output_dir, filename_stem,
                     **kwargs):
    """Drop-in replacement for ``core.tts_engine.synthesize`` used in tests."""
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{filename_stem}.{audio_format}")
    # Write a tiny but non-empty file so file_size / Content-Length is realistic.
    with open(path, "wb") as fh:
        fh.write(b"ID3" + b"\x00" * 128)
    voice = voices_module.get_voice(voice_id)
    return SynthesisResult(
        path=path,
        format=audio_format,
        engine=voice["engine"],
        voice_id=voice["id"],
        voice_name=voice["name"],
        file_size=os.path.getsize(path),
    )


class _BaseTest(TestCase):
    """Common setUp: isolated MEDIA_ROOT and fresh cache."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._tmp_media = tempfile.mkdtemp(prefix="tts_test_media_")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._tmp_media, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        cache.clear()
        self._media_override = override_settings(MEDIA_ROOT=self._tmp_media)
        self._media_override.enable()

    def tearDown(self):
        self._media_override.disable()


# ---------------------------------------------------------------------------
# Voices endpoint
# ---------------------------------------------------------------------------
class VoicesAPITests(_BaseTest):
    def test_list_all_voices(self):
        res = self.client.get("/api/voices/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["error_code"], 0)
        self.assertGreater(data["voices_count"], 0)
        self.assertIn("supported_audio_formats", data)
        self.assertIn("mp3", data["supported_audio_formats"])

    def test_filter_by_language(self):
        res = self.client.get("/api/voices/?language=ar")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["language"], "ar")
        self.assertGreaterEqual(data["voices_count"], 4)
        for voice in data["voices_detailed_list"]:
            self.assertEqual(voice["language"], "ar")
            self.assertIn(voice["engine"], {"edge", "gtts"})

    def test_unsupported_language(self):
        res = self.client.get("/api/voices/?language=xx")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["error_summary"], "LANGUAGE_NOT_SUPPORTED")

    def test_every_voice_is_real(self):
        """Catalog invariant: every voice has a backend mapping."""
        for voice in voices_module.VOICES_LIST:
            if voice["engine"] == "edge":
                self.assertTrue(voice.get("edge_voice"),
                                f"voice {voice['id']} missing edge_voice")
            elif voice["engine"] == "gtts":
                self.assertTrue(voice.get("gtts_lang"),
                                f"voice {voice['id']} missing gtts_lang")
            else:
                self.fail(f"voice {voice['id']} has unknown engine {voice['engine']}")


# ---------------------------------------------------------------------------
# Quota endpoint
# ---------------------------------------------------------------------------
class QuotaAPITests(_BaseTest):
    def test_initial_quota(self):
        res = self.client.get("/api/quota/")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["used"], 0)
        self.assertEqual(data["remaining"], data["daily_limit"])


# ---------------------------------------------------------------------------
# TTS endpoint — input validation & happy path
# ---------------------------------------------------------------------------
@mock.patch("core.views.synthesize", side_effect=_fake_synthesize)
class TTSAPITests(_BaseTest):
    def _post(self, body):
        return self.client.post(
            "/api/tts/", data=json.dumps(body), content_type="application/json",
        )

    def test_happy_path_arabic_voice(self, _mock):
        res = self._post({"text": "مرحبا", "voice_id": 1004, "audio_format": "mp3"})
        self.assertEqual(res.status_code, 200, res.content)
        data = res.json()
        self.assertEqual(data["error_code"], 0)
        self.assertEqual(data["voice"]["language"], "ar")
        self.assertTrue(data["audio_download_url"].endswith(".mp3"))
        self.assertGreater(data["file_size_bytes"], 0)
        self.assertEqual(data["quota"]["used"], len("مرحبا"))

    def test_missing_text(self, _mock):
        res = self._post({"voice_id": 1004})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["error_summary"], "POST_FIELD_ERROR")

    def test_missing_voice_id(self, _mock):
        res = self._post({"text": "hello"})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["error_summary"], "POST_FIELD_ERROR")

    def test_unknown_voice(self, _mock):
        res = self._post({"text": "hello", "voice_id": 999999})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["error_summary"], "VOICE_ID_ERROR")

    def test_invalid_json(self, _mock):
        res = self.client.post("/api/tts/", data="not json",
                               content_type="application/json")
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["error_summary"], "INVALID_JSON")

    def test_text_too_long(self, _mock):
        long_text = "a" * 6000  # > MAX_CHARS_PER_REQUEST=5000
        res = self._post({"text": long_text, "voice_id": 2002})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["error_summary"], "TEXT_LENGTH_ERROR")

    @override_settings(FFMPEG_AVAILABLE=False)
    def test_unsupported_format_when_no_ffmpeg(self, _mock):
        # Patch shutil.which so the engine reports ffmpeg as missing too.
        with mock.patch("core.tts_engine.shutil.which", return_value=None):
            res = self._post({"text": "hi", "voice_id": 2002, "audio_format": "wav"})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["error_summary"], "AUDIO_FORMAT_NOT_SUPPORTED")

    def test_numeric_field_validation(self, _mock):
        res = self._post({"text": "hi", "voice_id": 2002, "audio_speed": "fast"})
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.json()["error_summary"], "FIELD_TYPE_ERROR")


# ---------------------------------------------------------------------------
# TTS endpoint — quota / rate limiting
# ---------------------------------------------------------------------------
@mock.patch("core.views.synthesize", side_effect=_fake_synthesize)
class QuotaAndRateTests(_BaseTest):
    def _post(self, body):
        return self.client.post(
            "/api/tts/", data=json.dumps(body), content_type="application/json",
        )

    @override_settings(FREE_DAILY_CHAR_LIMIT=10, MAX_CHARS_PER_REQUEST=100)
    def test_quota_exhaustion(self, _mock):
        # First request: 7 chars, OK.
        r1 = self._post({"text": "1234567", "voice_id": 2002})
        self.assertEqual(r1.status_code, 200, r1.content)
        # Second request would need 5 chars but only 3 remain.
        r2 = self._post({"text": "abcde", "voice_id": 2002})
        self.assertEqual(r2.status_code, 429)
        self.assertEqual(r2.json()["error_summary"], "QUOTA_EXCEEDED")

    @override_settings(TTS_RATE_LIMIT_PER_MINUTE=2)
    def test_rate_limit(self, _mock):
        body = {"text": "hi", "voice_id": 2002}
        self.assertEqual(self._post(body).status_code, 200)
        self.assertEqual(self._post(body).status_code, 200)
        third = self._post(body)
        self.assertEqual(third.status_code, 429)
        self.assertEqual(third.json()["error_summary"], "RATE_LIMIT_EXCEEDED")


# ---------------------------------------------------------------------------
# Download endpoint — security
# ---------------------------------------------------------------------------
class DownloadTests(_BaseTest):
    def test_invalid_filename_pattern(self):
        # Wrong extension
        res = self.client.get("/api/download/evil.exe/")
        self.assertEqual(res.status_code, 404)

    def test_path_traversal_blocked(self):
        res = self.client.get("/api/download/..%2Fsettings.py/")
        self.assertEqual(res.status_code, 404)

    def test_missing_file(self):
        res = self.client.get("/api/download/tts_1_aaaaaaaa.mp3/")
        self.assertEqual(res.status_code, 404)

    def test_existing_file_served(self):
        # Create a file in the audio dir and request it.
        audio_dir = os.path.join(self._tmp_media, "audio")
        os.makedirs(audio_dir, exist_ok=True)
        fname = "tts_1_abcdef12.mp3"
        with open(os.path.join(audio_dir, fname), "wb") as fh:
            fh.write(b"ID3" + b"\x00" * 100)
        res = self.client.get(f"/api/download/{fname}/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res["Content-Type"], "audio/mpeg")
        # Drain the streaming response to keep the test runner happy on Windows.
        body = b"".join(res.streaming_content)
        self.assertGreater(len(body), 100)


# ---------------------------------------------------------------------------
# Engine smoke test (only when explicitly enabled — uses real network).
# ---------------------------------------------------------------------------
class EngineSmokeTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._enabled = os.environ.get("EDGE_TTS_LIVE") == "1"

    def test_edge_tts_real_synthesis(self):
        if not self._enabled:
            self.skipTest("Set EDGE_TTS_LIVE=1 to run live edge-tts test")
        from core.tts_engine import synthesize  # late import
        tmp = tempfile.mkdtemp(prefix="tts_live_")
        try:
            result = synthesize(
                text="hello world", voice_id=2002, audio_format="mp3",
                output_dir=tmp, filename_stem="live_test",
            )
            self.assertGreater(result.file_size, 1000)
            self.assertEqual(result.engine, "edge")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
