"""
Production views for TTSMaker Clone.

This module exposes a small, honest API:

* ``GET  /``                 -> main UI
* ``GET  /api/voices/``      -> real, curated voice catalog (edge-tts backed)
* ``POST /api/tts/``         -> generate speech, return a download URL
* ``GET  /api/quota/``       -> daily quota status for the current IP
* ``GET  /api/download/<filename>/`` -> stream generated file

All endpoints validate input, apply per-IP quota and rate limiting, and
return JSON errors with stable error codes.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
import uuid

from django.conf import settings
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .cleanup import cleanup_expired_audio
from .models import TTSConversion
from .quota import (
    check_and_increment_rate,
    get_client_ip,
    get_quota_status,
    reserve_quota,
)
from .tts_engine import (
    SynthesisResult,
    TTSEngineError,
    UnsupportedFormatError,
    ffmpeg_available,
    supported_formats,
    synthesize,
)
from .voices import (
    LANGUAGES,
    RTL_LANGUAGES,
    SUPPORTED_LANGUAGES,
    VOICES_LIST,
    get_voice,
    public_voice,
    voices_for_language,
    voices_grouped_by_language,
)

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Constants & validation
# ---------------------------------------------------------------------------
SAFE_FILENAME_RE = re.compile(r"^tts_[A-Za-z0-9_\-]+\.(mp3|wav|ogg|aac)$")
BREAK_TAG_RE = re.compile(r"\[\[break=\d+\]\]")
MAX_LINE_LENGTH = 50_000  # absolute upper-bound before any other check


def _error(code: str, message: str, status: int = 400, **extra) -> JsonResponse:
    payload = {
        "error_code": -1,
        "error_summary": code,
        "msg": message,
    }
    payload.update(extra)
    return JsonResponse(payload, status=status)


def _clean_text(raw: str, pause_time: int) -> str:
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    # Pause handling: numeric ms -> insert filler, -1 -> strip line breaks.
    if pause_time == -1:
        text = " ".join(line.strip() for line in text.split("\n") if line.strip())
    elif pause_time and pause_time > 0:
        text = " ... ".join(line.strip() for line in text.split("\n") if line.strip())
    # Strip explicit break tags; real prosody control is not yet wired.
    text = BREAK_TAG_RE.sub(" ", text)
    return text.strip()


# ---------------------------------------------------------------------------
# HTML pages
# ---------------------------------------------------------------------------
def index(request):
    """Main TTS conversion page."""
    grouped = voices_grouped_by_language()
    context = {
        "languages": LANGUAGES,
        "voices_grouped": grouped,
        "default_lang": "en",
        "free_char_limit": settings.FREE_DAILY_CHAR_LIMIT,
        "max_chars_per_request": settings.MAX_CHARS_PER_REQUEST,
        "supported_formats": sorted(supported_formats()),
        "supported_formats_json": json.dumps(sorted(supported_formats())),
        "ffmpeg_available": ffmpeg_available(),
        "rtl_languages_json": json.dumps(sorted(RTL_LANGUAGES)),
    }
    return render(request, "core/index.html", context)


def blog(request):
    return render(request, "core/blog.html")


def api_docs(request):
    return render(request, "core/api_docs.html", {
        "supported_formats": sorted(supported_formats()),
        "free_char_limit": settings.FREE_DAILY_CHAR_LIMIT,
        "max_chars_per_request": settings.MAX_CHARS_PER_REQUEST,
        "rate_limit": settings.TTS_RATE_LIMIT_PER_MINUTE,
    })


def privacy(request):
    return render(request, "core/privacy.html")


def terms(request):
    return render(request, "core/terms.html")


# ---------------------------------------------------------------------------
# API: voices list
# ---------------------------------------------------------------------------
@require_http_methods(["GET"])
def voices_api(request):
    """List available voices, optionally filtered by language."""
    language = request.GET.get("language") or None
    if language and language not in SUPPORTED_LANGUAGES:
        return _error("LANGUAGE_NOT_SUPPORTED",
                      f"Language '{language}' is not supported.")

    if language:
        grouped = {language: voices_for_language(language)}
        voices = [v for region_voices in grouped[language].values() for v in region_voices]
    else:
        voices = VOICES_LIST

    payload = {
        "error_code": 0,
        "error_summary": "",
        "msg": "Query the list of voices successfully.",
        "language": language or "all",
        "support_language_list": SUPPORTED_LANGUAGES,
        "voices_count": len(voices),
        "voices_id_list": [v["id"] for v in voices],
        "voices_detailed_list": [public_voice(v) for v in voices],
        "supported_audio_formats": sorted(supported_formats()),
        "ffmpeg_available": ffmpeg_available(),
    }
    return JsonResponse(payload)


# ---------------------------------------------------------------------------
# API: quota status
# ---------------------------------------------------------------------------
@require_http_methods(["GET"])
def quota_api(request):
    ip = get_client_ip(request)
    status = get_quota_status(ip)
    return JsonResponse({
        "error_code": 0,
        "error_summary": "",
        "ip": ip,
        "daily_limit": status.daily_limit,
        "used": status.used,
        "remaining": status.remaining,
        "reset_at": status.reset_at,
        "rate_limit_per_minute": settings.TTS_RATE_LIMIT_PER_MINUTE,
        "max_chars_per_request": settings.MAX_CHARS_PER_REQUEST,
    })


# ---------------------------------------------------------------------------
# API: TTS generation
# ---------------------------------------------------------------------------
@csrf_exempt
@require_http_methods(["POST"])
def tts_api(request):
    ip = get_client_ip(request)

    # Rate limit BEFORE doing any work.
    rate = check_and_increment_rate(ip)
    if not rate.allowed:
        return _error(
            "RATE_LIMIT_EXCEEDED",
            f"Too many requests. Limit is {rate.limit_per_minute} per minute.",
            status=429,
            retry_after=rate.retry_after,
        )

    # Parse JSON.
    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        return _error("INVALID_JSON", "Request body must be valid UTF-8 JSON.")

    text = (data.get("text") or "").strip()
    voice_id = data.get("voice_id")
    audio_format = (data.get("audio_format") or "mp3").lower()
    try:
        audio_speed = float(data.get("audio_speed", 1.0))
        audio_volume = float(data.get("audio_volume", 1.0))
        audio_pitch = float(data.get("audio_pitch", 1.0))
        pause_time = int(data.get("text_paragraph_pause_time", 0))
    except (TypeError, ValueError):
        return _error("FIELD_TYPE_ERROR",
                      "audio_speed/audio_volume/audio_pitch must be numbers; "
                      "text_paragraph_pause_time must be an integer.")

    if not text:
        return _error("POST_FIELD_ERROR", "Field 'text' is required.")
    if voice_id is None:
        return _error("POST_FIELD_ERROR", "Field 'voice_id' is required.")

    voice = get_voice(voice_id)
    if not voice:
        return _error("VOICE_ID_ERROR",
                      "Voice id does not exist. Call /api/voices/ to list valid ids.")

    # Per-request hard cap.
    if len(text) > settings.MAX_CHARS_PER_REQUEST:
        return _error(
            "TEXT_LENGTH_ERROR",
            f"Text length {len(text)} exceeds the per-request limit of "
            f"{settings.MAX_CHARS_PER_REQUEST} characters.",
        )

    if len(text) > voice["text_characters_limit"]:
        return _error(
            "TEXT_LENGTH_ERROR",
            f"Text exceeds this voice's limit of {voice['text_characters_limit']} characters.",
        )

    # Validate format BEFORE consuming quota.
    if audio_format not in supported_formats():
        return _error(
            "AUDIO_FORMAT_NOT_SUPPORTED",
            f"Audio format '{audio_format}' is not supported on this server. "
            f"Supported: {sorted(supported_formats())}",
            supported_audio_formats=sorted(supported_formats()),
            ffmpeg_available=ffmpeg_available(),
        )

    # Reserve quota.
    granted, quota_status = reserve_quota(ip, len(text))
    if not granted:
        return _error(
            "QUOTA_EXCEEDED",
            f"Daily quota exceeded. Limit is {quota_status.daily_limit} characters per day.",
            status=429,
            quota={
                "daily_limit": quota_status.daily_limit,
                "used": quota_status.used,
                "remaining": quota_status.remaining,
                "reset_at": quota_status.reset_at,
            },
        )

    # Prepare cleaned text & filename.
    cleaned = _clean_text(text, pause_time)
    if not cleaned:
        return _error("POST_FIELD_ERROR", "Text is empty after cleaning.")

    timestamp = int(time.time())
    stem = f"tts_{timestamp}_{uuid.uuid4().hex[:8]}"
    output_dir = os.path.join(settings.MEDIA_ROOT, "audio")

    try:
        result: SynthesisResult = synthesize(
            text=cleaned,
            voice_id=voice["id"],
            audio_format=audio_format,
            speed=audio_speed,
            volume=audio_volume,
            pitch=audio_pitch,
            output_dir=output_dir,
            filename_stem=stem,
        )
    except UnsupportedFormatError as exc:
        return _error("AUDIO_FORMAT_NOT_SUPPORTED", str(exc),
                      supported_audio_formats=sorted(supported_formats()))
    except TTSEngineError as exc:
        log.warning("TTS engine failed for ip=%s voice=%s: %s", ip, voice["id"], exc)
        return _error("ENGINE_ERROR",
                      "Speech synthesis failed. Please try again in a few seconds.",
                      status=502)
    except Exception:
        log.exception("Unexpected synthesis failure")
        return _error("INTERNAL_ERROR", "Internal server error.", status=500)

    # Persist a record for analytics / admin (no raw text by default for privacy).
    filename = os.path.basename(result.path)
    try:
        TTSConversion.objects.create(
            text=cleaned[:500],  # store only a preview, not the full payload
            language=voice["language"],
            voice_id=str(voice["id"]),
            speed=audio_speed,
            volume=audio_volume,
            audio_file=f"audio/{filename}",
            file_format=result.format,
            file_size=result.file_size,
            ip_address=ip,
        )
    except Exception:
        log.exception("Failed to persist TTSConversion record (non-fatal)")

    # Best-effort cleanup of old files.
    try:
        cleanup_expired_audio()
    except Exception:
        log.exception("Cleanup pass failed (non-fatal)")

    download_url = request.build_absolute_uri(f"/api/download/{filename}")

    return JsonResponse({
        "error_code": 0,
        "error_summary": "",
        "msg": "TTS task executed successfully.",
        "tts_task_characters_count": len(cleaned),
        "voice": public_voice(voice),
        "audio_download_url": download_url,
        "audio_file_format": result.format,
        "engine_used": result.engine,
        "file_size_bytes": result.file_size,
        "current_timestamp": timestamp,
        "audio_file_expiration_timestamp": timestamp + settings.AUDIO_FILE_TTL_SECONDS,
        "quota": {
            "daily_limit": quota_status.daily_limit,
            "used": quota_status.used,
            "remaining": quota_status.remaining,
            "reset_at": quota_status.reset_at,
        },
    })


# ---------------------------------------------------------------------------
# API: download
# ---------------------------------------------------------------------------
_MIME = {
    "mp3": "audio/mpeg",
    "wav": "audio/wav",
    "ogg": "audio/ogg",
    "aac": "audio/aac",
}


def download_audio(request, filename: str):
    """Stream a previously generated audio file."""
    if not SAFE_FILENAME_RE.match(filename):
        raise Http404("Invalid filename.")

    audio_dir = os.path.join(settings.MEDIA_ROOT, "audio")
    file_path = os.path.normpath(os.path.join(audio_dir, filename))
    if not file_path.startswith(os.path.normpath(audio_dir) + os.sep):
        raise Http404("Invalid path.")
    if not os.path.exists(file_path):
        raise Http404("Audio file not found or expired.")

    ext = filename.rsplit(".", 1)[-1].lower()
    content_type = _MIME.get(ext, "application/octet-stream")
    response = FileResponse(open(file_path, "rb"), content_type=content_type)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
