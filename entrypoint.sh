#!/bin/sh
set -e

echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput

echo "Starting server..."
exec gunicorn src.config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120