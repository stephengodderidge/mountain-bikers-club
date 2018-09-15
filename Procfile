release: python manage.py migrate
web: gunicorn mountainbikers.wsgi
worker: REMAP_SIGTERM=SIGQUIT celery -A mountainbikers worker
