FROM python:3.12-slim

# System deps: ffmpeg unlocks wav/ogg/aac conversion.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg curl \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install Python deps first for better layer caching.
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app

# Production-safe defaults; override at runtime.
ENV DJANGO_DEBUG=False \
    DJANGO_ALLOWED_HOSTS=* \
    FFMPEG_AVAILABLE=True \
    PORT=8000

# Collect static files into staticfiles/ for WhiteNoise.
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/api/voices/?language=en >/dev/null || exit 1

CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn ttsmaker_clone.wsgi:application --workers 3 --threads 2 --bind 0.0.0.0:${PORT} --access-logfile - --error-logfile -"]
