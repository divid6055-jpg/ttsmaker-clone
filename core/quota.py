"""
Per-IP daily quota tracking and lightweight rate limiting.

Uses Django's cache backend, so it is process-local with the default LocMem
backend but transparently scales when the project is configured with Redis
or memcached. Keys are namespaced and expire automatically.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Tuple

from django.conf import settings
from django.core.cache import cache


_QUOTA_KEY = "tts:quota:{ip}:{day}"
_RATE_KEY = "tts:rate:{ip}:{minute}"

ONE_DAY = 60 * 60 * 24


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_client_ip(request) -> str:
    """Resolve the client's IP, honouring a configured proxy header if any."""
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "0.0.0.0")


def _today_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d")


def _minute_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M")


def _seconds_until_tomorrow() -> int:
    now = datetime.now(timezone.utc)
    tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp() + ONE_DAY
    return max(60, int(tomorrow - now.timestamp()))


# ---------------------------------------------------------------------------
# Public dataclasses
# ---------------------------------------------------------------------------
@dataclass
class QuotaStatus:
    daily_limit: int
    used: int
    remaining: int
    reset_at: int  # unix timestamp


@dataclass
class RateStatus:
    limit_per_minute: int
    used: int
    allowed: bool
    retry_after: int  # seconds


# ---------------------------------------------------------------------------
# Quota
# ---------------------------------------------------------------------------
def get_quota_status(ip: str) -> QuotaStatus:
    limit = int(getattr(settings, "FREE_DAILY_CHAR_LIMIT", 20000))
    key = _QUOTA_KEY.format(ip=ip, day=_today_key())
    used = int(cache.get(key, 0))
    remaining = max(0, limit - used)
    reset_at = int(time.time()) + _seconds_until_tomorrow()
    return QuotaStatus(daily_limit=limit, used=used, remaining=remaining, reset_at=reset_at)


def reserve_quota(ip: str, chars: int) -> Tuple[bool, QuotaStatus]:
    """Atomically reserve ``chars`` of quota for ``ip``.

    Returns (granted, status). When granted is False, ``status`` reflects the
    state *before* the rejected request.
    """
    status = get_quota_status(ip)
    if chars <= 0:
        return True, status
    if chars > status.remaining:
        return False, status

    key = _QUOTA_KEY.format(ip=ip, day=_today_key())
    # ``incr`` raises if the key doesn't exist; seed it first.
    try:
        new_used = cache.incr(key, chars)
    except ValueError:
        cache.set(key, chars, timeout=_seconds_until_tomorrow())
        new_used = chars
    new_status = QuotaStatus(
        daily_limit=status.daily_limit,
        used=int(new_used),
        remaining=max(0, status.daily_limit - int(new_used)),
        reset_at=status.reset_at,
    )
    return True, new_status


# ---------------------------------------------------------------------------
# Rate limiting (per minute, per IP)
# ---------------------------------------------------------------------------
def check_and_increment_rate(ip: str) -> RateStatus:
    limit = int(getattr(settings, "TTS_RATE_LIMIT_PER_MINUTE", 10))
    key = _RATE_KEY.format(ip=ip, minute=_minute_key())
    try:
        new_count = cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=65)
        new_count = 1
    allowed = new_count <= limit
    retry_after = 0 if allowed else 60
    return RateStatus(
        limit_per_minute=limit,
        used=int(new_count),
        allowed=allowed,
        retry_after=retry_after,
    )
