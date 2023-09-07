web: daphne metazo.asgi:application --port $PORT --bind 0.0.0.0 -v2
worker: python manage.py runworker --settings=metazo.settings -v2
celery: celery -A metazo worker -l INFO
beat: celery -A metazo beat -l INFO
release: python manage.py migrate --noinput
