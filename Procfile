web: python manage.py migrate && python manage.py collectstatic --noinput && python -m daphne realtime_questions.asgi:application --bind 0.0.0.0 --port $PORT
