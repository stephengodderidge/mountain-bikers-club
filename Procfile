release: python manage.py migrate
web: daphne mountainbikers.asgi:application --port $PORT --bind 0.0.0.0
