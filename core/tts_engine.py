"""
Real TTS engine wrapper.

Provides a single ``synthesize`` entry point that produces an MP3 file using
either edge-tts (Microsoft Azure neural voices) or gTTS as a fallback.

Optional post-processing converts the MP3 to other formats (wav/ogg/aac) via
pydub + ffmpeg. If ffmpeg is not available the API will refuse non-MP3
formats up-front rather than silently mislabelling a file.
"""

from __future__ import annotations

import asyncio
import logging
import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Optional

from django.conf import settings

from .voices import get_voice

log = logging.getLogger(__name__)


class TTSEngineError(Exception):
    """Raised when synthesis fails for an expected reason (e.g. network)."""


class UnsupportedFormatError(Exception):
    """Raised when the requested audio format is not supported on this host."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
SUPPORTED_FORMATS_NATIVE = {"mp3"}
SUPPORTED_FORMATS_WITH_FFMPEG = {"mp3", "wav", "ogg", "aac"}


def ffmpeg_available() -> bool:
    """Return True if ffmpeg is on PATH (cached on settings.FFMPEG_AVAILABLE)."""
    configured = getattr(settings, "FFMPEG_AVAILABLE", False)
    if configured:
        return True
    return shutil.which("ffmpeg") is not None


def supported_formats() -> set:
    return SUPPORTED_FORMATS_WITH_FFMPEG if ffmpeg_available() else SUPPORTED_FORMATS_NATIVE


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(value)))


def _percent(value: float) -> str:
    """Convert a multiplier (1.0 == default) to edge-tts percentage string."""
    delta = int(round((value - 1.0) * 100))
    sign = "+" if delta >= 0 else "-"
    return f"{sign}{abs(delta)}%"


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------
@dataclass
class SynthesisResult:
    path: str
    format: str
    engine: str
    voice_id: int
    voice_name: str
    file_size: int


# ---------------------------------------------------------------------------
# Engine implementations
# ---------------------------------------------------------------------------
async def _edge_synthesize(text: str, edge_voice: str, mp3_path: str,
                           speed: float = 1.0, volume: float = 1.0,
                           pitch: float = 1.0) -> None:
    import edge_tts  # imported lazily so test envs without it can still load module

    rate = _percent(speed)
    vol = _percent(volume)
    # edge-tts pitch is in Hz; convert from a multiplier centred at 1.0
    pitch_hz = int(round((pitch - 1.0) * 50))
    pitch_str = f"{'+' if pitch_hz >= 0 else '-'}{abs(pitch_hz)}Hz"

    communicate = edge_tts.Communicate(
        text=text,
        voice=edge_voice,
        rate=rate,
        volume=vol,
        pitch=pitch_str,
    )
    await communicate.save(mp3_path)


def _gtts_synthesize(text: str, gtts_lang: str, mp3_path: str,
                     speed: float = 1.0) -> None:
    from gtts import gTTS

    slow = speed < 0.85
    tts = gTTS(text=text, lang=gtts_lang, slow=slow)
    tts.save(mp3_path)


def _convert_mp3_to(target_path: str, mp3_path: str, fmt: str) -> None:
    """Convert MP3 to another format using pydub + ffmpeg."""
    from pydub import AudioSegment

    audio = AudioSegment.from_file(mp3_path, format="mp3")
    # pydub passes the format string to ffmpeg as -f, so keep names canonical.
    audio.export(target_path, format=fmt)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def synthesize(
    *,
    text: str,
    voice_id: int,
    audio_format: str = "mp3",
    speed: float = 1.0,
    volume: float = 1.0,
    pitch: float = 1.0,
    output_dir: str,
    filename_stem: str,
) -> SynthesisResult:
    """Generate speech audio for the given voice.

    Returns a :class:`SynthesisResult` with the path to the final file. Raises
    :class:`UnsupportedFormatError` if the requested format requires ffmpeg
    and ffmpeg is not available, or :class:`TTSEngineError` for runtime issues.
    """
    voice = get_voice(voice_id)
    if not voice:
        raise TTSEngineError(f"Voice id {voice_id} is not in the catalog.")

    audio_format = (audio_format or "mp3").lower()
    if audio_format not in SUPPORTED_FORMATS_WITH_FFMPEG:
        raise UnsupportedFormatError(
            f"Unsupported audio format '{audio_format}'. "
            f"Allowed formats: {sorted(SUPPORTED_FORMATS_WITH_FFMPEG)}"
        )

    if audio_format != "mp3" and not ffmpeg_available():
        raise UnsupportedFormatError(
            "Conversion to '%s' requires ffmpeg, which is not installed on this server. "
            "Use 'mp3' or install ffmpeg." % audio_format
        )

    # Clamp ranges so we never send weird values to the engine.
    speed = _clamp(speed, 0.5, 2.0)
    volume = _clamp(volume, 0.5, 2.0)
    pitch = _clamp(pitch, 0.5, 2.0)

    os.makedirs(output_dir, exist_ok=True)
    mp3_path = os.path.join(output_dir, f"{filename_stem}.mp3")

    engine = voice["engine"]
    try:
        if engine == "edge":
            asyncio.run(
                _edge_synthesize(
                    text=text,
                    edge_voice=voice["edge_voice"],
                    mp3_path=mp3_path,
                    speed=speed,
                    volume=volume,
                    pitch=pitch,
                )
            )
        elif engine == "gtts":
            _gtts_synthesize(text=text, gtts_lang=voice["gtts_lang"], mp3_path=mp3_path, speed=speed)
        else:
            raise TTSEngineError(f"Unknown engine '{engine}' for voice {voice_id}.")
    except UnsupportedFormatError:
        raise
    except Exception as exc:  # network errors, codec errors, etc.
        log.exception("TTS synthesis failed for voice %s", voice_id)
        # If edge-tts fails AND a gtts fallback exists, try it once.
        if engine == "edge" and voice.get("gtts_lang"):
            try:
                _gtts_synthesize(text=text, gtts_lang=voice["gtts_lang"],
                                 mp3_path=mp3_path, speed=speed)
                engine = "gtts-fallback"
            except Exception as exc2:
                raise TTSEngineError(
                    f"Both edge-tts and gTTS failed: edge={exc!r}; gtts={exc2!r}"
                )
        else:
            raise TTSEngineError(f"TTS synthesis failed: {exc!r}")

    final_path = mp3_path
    if audio_format != "mp3":
        target_path = os.path.join(output_dir, f"{filename_stem}.{audio_format}")
        try:
            _convert_mp3_to(target_path, mp3_path, audio_format)
        except Exception as exc:
            log.exception("Audio conversion to %s failed", audio_format)
            raise TTSEngineError(f"Audio conversion to {audio_format} failed: {exc!r}")
        # Remove the intermediate MP3 to save disk.
        try:
            os.remove(mp3_path)
        except OSError:
            pass
        final_path = target_path

    if not os.path.exists(final_path):
        raise TTSEngineError("Synthesis produced no output file.")

    return SynthesisResult(
        path=final_path,
        format=audio_format,
        engine=engine,
        voice_id=voice["id"],
        voice_name=voice["name"],
        file_size=os.path.getsize(final_path),
    )
