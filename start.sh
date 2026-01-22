#!/usr/bin/env bash
set -e

echo "Running collectstatic..."
python manage.py collectstatic --noinput

echo "Starting Daphne..."
exec python -m daphne realtime_questions.asgi:application --bind 0.0.0.0 --port $PORT
