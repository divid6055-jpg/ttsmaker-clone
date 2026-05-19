# Final Report — TTSMaker Clone Hardening

## Goal
Transform the repo from a static, partially-faked TTSMaker clone into a small but production-ready TTS web app.

## Result at a glance
| Item                                          | Before                                          | After                                                                                                                  |
|-----------------------------------------------|--------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| Voice catalog                                  | ~500 voice IDs, almost all fake                  | Curated **102 real voices** across 22 languages, each backed by a real `edge-tts` neural voice or `gTTS` language     |
| Audio format selection                         | UI offered MP3/WAV/OGG/AAC, server returned MP3  | Real conversion via `pydub` + `ffmpeg`; falls back to MP3-only and *says so* when ffmpeg is missing                    |
| `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`         | Hardcoded, insecure                              | Driven by env vars; safe defaults; HSTS/SSL redirect/cookie flags activated when `DEBUG=False`                         |
| CORS                                           | `CORS_ALLOW_ALL_ORIGINS=True`                    | Explicit allow-list via `DJANGO_CORS_ALLOWED_ORIGINS`; permissive only in `DEBUG`                                      |
| Quota                                          | `FREE_CHAR_LIMIT` constant, cosmetic only        | **Real per-IP daily char quota** backed by cache, returned in API responses, auto-reset at midnight UTC                |
| Rate limiting                                  | None                                             | **Per-IP per-minute limit** enforced *before* synthesis; returns 429 + `retry_after`                                   |
| File cleanup                                   | Files lived forever                              | Throttled background cleanup after each request; lifetime = `AUDIO_FILE_TTL_SECONDS`                                   |
| Download safety                                | Open path concatenation                          | Strict filename regex; path-traversal blocked; correct MIME per format                                                 |
| Arabic / RTL                                   | 4 fake "Arabic" entries, no RTL handling         | 16 real Arabic voices (Egypt, Saudi, UAE, Jordan, Lebanon, Iraq, Syria, Tunisia) + automatic `dir=rtl`                |
| Tests                                          | None                                             | **20 fast offline tests** covering voices, quota, rate limit, validation, downloads + optional live engine smoke test |
| Frontend assets                                | 1192-line CSS, 655-line JS with mirrored data    | 210-line CSS, 260-line JS — voices fetched from API, no parallel mirror                                                |
| Deployment artifacts                           | None                                             | `.env.example`, `Dockerfile`, `Procfile`, systemd unit, nginx config, README walkthrough                              |

## Critical findings — addressed

1. **Fake/mirrored voice IDs.** Replaced the entire `VOICES` dict with `core/voices.py`. Every entry has either `edge_voice` (Microsoft Azure neural) or `gtts_lang` (Google fallback) and is verified by a test invariant: `test_every_voice_is_real`.
2. **Unsafe production defaults.** `ttsmaker_clone/settings.py` rewritten to read secrets, `DEBUG`, hosts, CSRF/CORS origins, security headers from env. `.env.example` documents every variable.
3. **Misleading audio format.** New `core/tts_engine.py` performs real conversion using `pydub` + `ffmpeg`. When ffmpeg is absent, `/api/voices/` exposes `supported_audio_formats: ["mp3"]` and `/api/tts/` returns `AUDIO_FORMAT_NOT_SUPPORTED` for any other format — no silent mislabelling.
4. **Cosmetic quota.** `core/quota.py` implements actual per-IP daily tracking via the cache. Quota is reserved **before** synthesis so abusive callers can't burn engine time over the limit. `/api/quota/` exposes live status to the UI.
5. **No rate limiting, validation, cleanup, error handling.** All added:
   - `core/quota.check_and_increment_rate` (per-IP/minute, returns 429 + `retry_after`).
   - Strict input validation (`POST_FIELD_ERROR`, `FIELD_TYPE_ERROR`, `TEXT_LENGTH_ERROR`, `VOICE_ID_ERROR`, `AUDIO_FORMAT_NOT_SUPPORTED`, `INVALID_JSON`).
   - `core/cleanup.cleanup_expired_audio` (throttled to once/minute, thread-safe).
   - Try/except around engine calls returns `ENGINE_ERROR` 502 instead of raw stack traces.
6. **Arabic / RTL.** Added 16 real Arabic neural voices (8 dialects × 2 genders). UI flips `dir=rtl` on the `<html>` and textarea automatically when an RTL language is picked; CSS uses Cairo font for RTL, Inter for LTR.
7. **Real tests.** `core/tests.py` covers all the failure paths called out in the brief (voice list, generation, quota, download, invalid inputs) plus security and the catalog invariant. 20 tests, <1 s, no network needed. An opt-in `EDGE_TTS_LIVE=1` smoke test verifies the real engine end-to-end.
8. **Frontend UX.** Index page rewritten with semantic HTML, accessible labels, skip link, range sliders for speed/volume/pitch, status box, result card with player + download link. The 600+ lines of mirrored fake voice data in JS were deleted — voices now come exclusively from `/api/voices/`.
9. **Deployment-ready setup.** `.env.example`, `Dockerfile`, `Procfile`, systemd unit, nginx config, comprehensive README with 7-step deployment walkthrough.
10. **Code quality.** Modules are small and focused (`voices`, `tts_engine`, `quota`, `cleanup`, `views`). Logging is structured. Sensitive data (full submitted text) is no longer stored — only the first 500 chars are kept in `TTSConversion` for analytics, and audio files are deleted automatically.

## How to run

```bash
git clone https://github.com/divid6055-jpg/ttsmaker-clone.git
cd ttsmaker-clone
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then edit
python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000/>. Pick "العربية (Arabic)" — the UI will flip to RTL and load 16 real Arabic voices.

## How to deploy

Full step-by-step in [README.md](README.md). Short version:

```bash
# 1. Install ffmpeg, clone, create virtualenv, pip install
# 2. cp .env.example .env  &&  edit (set DJANGO_SECRET_KEY, DEBUG=False, hosts, CORS, CSRF origins)
# 3. python manage.py migrate
# 4. python manage.py collectstatic --noinput
# 5. gunicorn ttsmaker_clone.wsgi:application --workers 3 --threads 2 --bind 0.0.0.0:8000
# 6. nginx in front (see deploy/nginx.conf.example), TLS via certbot
# 7. Enable SECURE_SSL_REDIRECT, *_COOKIE_SECURE, HSTS once HTTPS is stable
```

## Verification commands you can run today

```bash
# All tests (offline, < 1s)
DJANGO_DEBUG=True DJANGO_SECRET_KEY=test-key python manage.py test core

# Deploy-mode sanity check
python manage.py check --deploy

# Real Arabic TTS via the API
curl -s -X POST http://127.0.0.1:8000/api/tts/ \
  -H "Content-Type: application/json" \
  -d '{"text":"مرحبا، أهلاً بك","voice_id":1004,"audio_format":"mp3"}'
```

## What was deliberately *not* done

- **No SSML / per-word prosody control.** edge-tts supports it but the upstream TTSMaker UI exposed a half-baked `[[break=N]]` syntax. We strip those tags instead of pretending we honour them. Adding real SSML is a future enhancement.
- **No user accounts / paid tier.** The pricing/PRO UI was vapor and was removed. Self-hosters who need accounts can wire up Django's auth system.
- **No multi-emotion presets.** Edge voices that support styles via SSML are still single-style here. This avoids advertising features that the current pipeline doesn't deliver.
- **No CDN/object storage for audio files.** Files live in local `MEDIA_ROOT` and are cleaned up after the TTL. If you need horizontal scaling, swap in S3 + a Celery cleanup job.

These omissions were intentional and documented rather than hidden behind fake UI.

## Commit history (high-level)

```
Stage 1  Production-ready security settings (env vars, headers, CORS allow-list)
Stage 2-5  Real edge-tts engine, honest voice catalog, ffmpeg conversion, real quota, rate limit
Stage 6-7  Rewrite frontend (clean UX, real RTL, no fake voices), templates trimmed
Stage 8    Add 20-test suite + initial migration
Stage 9    README, Dockerfile, Procfile, systemd unit, nginx config
```

Each stage was committed and pushed to `main` in order, per the engagement rules.
