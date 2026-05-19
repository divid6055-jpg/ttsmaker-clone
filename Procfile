web: gunicorn ttsmaker_clone.wsgi:application --workers 3 --threads 2 --bind 0.0.0.0:${PORT:-8000} --access-logfile - --error-logfile -
release: python manage.py migrate --noinput && python manage.py collectstatic --noinput
