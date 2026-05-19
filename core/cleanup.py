"""Background cleanup of expired audio files."""

from __future__ import annotations

import logging
import os
import threading
import time

from django.conf import settings

log = logging.getLogger(__name__)

_lock = threading.Lock()
_last_run = 0.0


def cleanup_expired_audio(max_age_seconds: int | None = None) -> int:
    """Delete audio files older than ``max_age_seconds``.

    Returns the number of files removed. Safe to call concurrently (cheap
    in-process lock). Designed to be invoked opportunistically after each
    successful TTS generation.
    """
    global _last_run

    if max_age_seconds is None:
        max_age_seconds = int(getattr(settings, "AUDIO_FILE_TTL_SECONDS", 7200))

    # Don't run more than once per minute.
    now = time.time()
    with _lock:
        if now - _last_run < 60:
            return 0
        _last_run = now

    audio_dir = os.path.join(settings.MEDIA_ROOT, "audio")
    if not os.path.isdir(audio_dir):
        return 0

    removed = 0
    cutoff = now - max_age_seconds
    for entry in os.scandir(audio_dir):
        if not entry.is_file():
            continue
        try:
            if entry.stat().st_mtime < cutoff:
                os.remove(entry.path)
                removed += 1
        except OSError:
            log.debug("Could not remove expired file %s", entry.path, exc_info=True)
    if removed:
        log.info("Cleaned up %d expired audio file(s)", removed)
    return removed
