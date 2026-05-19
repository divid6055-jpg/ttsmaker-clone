# TTSMaker Clone

A production-ready, open-source text-to-speech web application built on Django, with **real Microsoft Azure neural voices** (via [`edge-tts`](https://github.com/rany2/edge-tts)) and a gTTS fallback. It started as a static clone of TTSMaker.com and has been hardened into a usable, honest TTS service.

> **What changed in this rewrite (one-line):** every voice now corresponds to a real backend voice, every advertised audio format actually works, secrets and CORS are no longer hardcoded, and quota/rate limits are real — not cosmetic.

---

## Features

- **Real neural voices.** Curated catalog of Microsoft Azure neural voices through `edge-tts`. No mirrored or fake voice IDs.
- **22+ languages**, including full Arabic coverage (Egypt, Saudi Arabia, UAE, Jordan, Lebanon, Iraq, Syria, Tunisia), plus English (US/UK/AU/CA/IN), Spanish, French, German, Italian, Portuguese, Russian, Turkish, Japanese, Korean, Chinese (Mainland/HK/TW), Hindi, Urdu, Persian, Hebrew, Dutch, Polish, Swedish, Indonesian, Thai, Vietnamese.
- **RTL aware UI.** The interface flips to right-to-left automatically for Arabic, Urdu, Persian and Hebrew.
- **Honest audio formats.** MP3 always works. WAV / OGG / AAC are offered only when `ffmpeg` is available and conversion is performed by `pydub` + `ffmpeg`. The API auto-detects this and reports it via `/api/voices/`.
- **Production-hardened.** Secret key, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and CORS are all driven by environment variables. Security headers (HSTS, X-Frame-Options, content-type, referrer-policy) turn on automatically when `DJANGO_DEBUG=False`.
- **Real per-IP daily quota** (default 20 000 chars / day) and **per-minute rate limit** (default 10 req/min), both backed by Django's cache.
- **File cleanup.** Generated audio files are deleted after `AUDIO_FILE_TTL_SECONDS` (default 2 hours) on every successful request (throttled to once per minute).
- **20 fast, offline tests** covering voices, quota, rate-limit, validation, download security, and a live smoke test you can opt into.

---

## API

| Method | Path                                | Purpose                                |
|--------|-------------------------------------|----------------------------------------|
| GET    | `/api/voices/?language=<code>`      | List real voices (filter optional)     |
| GET    | `/api/quota/`                       | Inspect daily quota for the caller IP  |
| POST   | `/api/tts/`                         | Synthesize speech                      |
| GET    | `/api/download/<filename>/`         | Stream a generated audio file          |

Full reference at `/api-docs/` once the app is running. Example:

```bash
curl -X POST http://localhost:8000/api/tts/ \
  -H "Content-Type: application/json" \
  -d '{"text":"مرحبا بالعالم","voice_id":1004,"audio_format":"mp3"}'
```

Stable error codes: `INVALID_JSON`, `POST_FIELD_ERROR`, `VOICE_ID_ERROR`, `TEXT_LENGTH_ERROR`, `AUDIO_FORMAT_NOT_SUPPORTED`, `RATE_LIMIT_EXCEEDED`, `QUOTA_EXCEEDED`, `ENGINE_ERROR`.

---

## Quick start (local development)

Requirements: Python 3.10+, optionally `ffmpeg` if you want WAV/OGG/AAC output.

```bash
git clone https://github.com/divid6055-jpg/ttsmaker-clone.git
cd ttsmaker-clone

python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env                # then edit values
python manage.py migrate
python manage.py runserver
```

Open <http://127.0.0.1:8000/> in your browser.

Optional: `sudo apt install ffmpeg` (or `brew install ffmpeg`) to unlock WAV / OGG / AAC.

---

## Running the tests

```bash
DJANGO_DEBUG=True DJANGO_SECRET_KEY=test-key python manage.py test core
```

All 20 tests should pass in under a second. Mocks are used in place of network calls so the suite works offline.

To run a real (online) edge-tts smoke test:

```bash
EDGE_TTS_LIVE=1 python manage.py test core.tests.EngineSmokeTest
```

---

## Configuration

Everything is configured through environment variables. See [`.env.example`](.env.example) for the full annotated list. The most important ones:

| Variable                          | Default                       | Purpose                                              |
|-----------------------------------|-------------------------------|------------------------------------------------------|
| `DJANGO_SECRET_KEY`               | *insecure dev fallback*       | **Required in production.** Cryptographic key.       |
| `DJANGO_DEBUG`                    | `False`                       | Never set to `True` in production.                   |
| `DJANGO_ALLOWED_HOSTS`            | `127.0.0.1,localhost`         | Comma-separated host names.                          |
| `DJANGO_CSRF_TRUSTED_ORIGINS`     | empty                         | e.g. `https://your-domain.com`.                      |
| `DJANGO_CORS_ALLOWED_ORIGINS`     | empty                         | When empty *and* `DEBUG=True`, all origins allowed.  |
| `TTS_DEFAULT_ENGINE`              | `edge`                        | `edge` or `gtts`.                                    |
| `FFMPEG_AVAILABLE`                | autodetect                    | Force-disable conversion if you know ffmpeg is gone. |
| `FREE_DAILY_CHAR_LIMIT`           | `20000`                       | Per-IP daily character quota.                        |
| `MAX_CHARS_PER_REQUEST`           | `5000`                        | Hard cap per individual request.                     |
| `TTS_RATE_LIMIT_PER_MINUTE`       | `10`                          | Per-IP rate limit.                                   |
| `AUDIO_FILE_TTL_SECONDS`          | `7200`                        | Audio file lifetime before background cleanup.       |
| `SECURE_SSL_REDIRECT`             | `False`                       | Enable behind HTTPS terminating proxy.               |
| `SECURE_HSTS_SECONDS`             | `0`                           | Set to e.g. `31536000` once HTTPS is stable.         |

---

## Production deployment

### 1 — Install system dependencies

```bash
sudo apt update
sudo apt install -y python3-pip python3-venv ffmpeg
```

`ffmpeg` is **optional**, but without it the API will reject non-MP3 formats. It is recommended.

### 2 — Set up the application

```bash
git clone https://github.com/divid6055-jpg/ttsmaker-clone.git /opt/ttsmaker-clone
cd /opt/ttsmaker-clone
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3 — Configure environment

```bash
cp .env.example .env
# Generate a strong secret key:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# Edit .env: DJANGO_SECRET_KEY, DJANGO_DEBUG=False, DJANGO_ALLOWED_HOSTS,
#           DJANGO_CSRF_TRUSTED_ORIGINS, DJANGO_CORS_ALLOWED_ORIGINS
```

### 4 — Migrate & collect static files

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

Static files are served by [WhiteNoise](http://whitenoise.evans.io/) (already wired into `MIDDLEWARE`), so you do not need a separate static file server.

### 5 — Run with Gunicorn

```bash
gunicorn ttsmaker_clone.wsgi:application \
    --workers 3 --threads 2 \
    --bind 0.0.0.0:8000 \
    --access-logfile - --error-logfile -
```

The repository ships a ready-made `Procfile` and an example `systemd` unit (see [`deploy/`](deploy/)) you can adapt.

### 6 — Front with nginx (recommended)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    client_max_body_size 2m;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Then add HTTPS via Certbot (`sudo certbot --nginx`) and set `SECURE_SSL_REDIRECT=True`, `SESSION_COOKIE_SECURE=True`, `CSRF_COOKIE_SECURE=True`, `SECURE_HSTS_SECONDS=31536000`.

### 7 — Docker (alternative)

A `Dockerfile` is included:

```bash
docker build -t ttsmaker-clone .
docker run --rm -p 8000:8000 \
  -e DJANGO_SECRET_KEY="$(openssl rand -hex 32)" \
  -e DJANGO_ALLOWED_HOSTS="*" \
  ttsmaker-clone
```

---

## Project structure

```
ttsmaker-clone/
├── core/
│   ├── voices.py          # Curated voice catalog (real edge-tts mappings)
│   ├── tts_engine.py      # Synthesis + format conversion
│   ├── quota.py           # Daily quota + rate limit
│   ├── cleanup.py         # Background-on-write cleanup
│   ├── views.py           # API + page views
│   ├── models.py          # TTSConversion analytics record
│   ├── tests.py           # 20 tests, all offline
│   └── migrations/
├── ttsmaker_clone/        # Django project (settings, urls, wsgi/asgi)
├── templates/core/        # HTML pages
├── static/                # CSS / JS
├── deploy/                # Sample Procfile / systemd / Dockerfile
├── .env.example
├── requirements.txt
└── manage.py
```

---

## Security notes

- **Never** ship with `DJANGO_DEBUG=True` or the dev secret key.
- The download endpoint validates filenames with a strict regex and refuses path traversal.
- `TTSConversion` only persists the first 500 characters of the submitted text for analytics; the full payload lives only as long as the resulting audio file does.
- Rate limit and quota are enforced *before* synthesis, so abusive callers can't run the engine even once over the limit.
- Cookies are flagged `Secure` and `HttpOnly` automatically when `DEBUG=False` and the corresponding env vars are enabled.

---

## License

MIT. See [LICENSE](LICENSE) if present, otherwise use freely with attribution to the upstream services (`edge-tts`, `gTTS`).
