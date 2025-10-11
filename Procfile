web: python manage.py migrate && python manage.py setup_templates && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 2 --timeout 120 --worker-class gthread --access-logfile - --error-logfile - --log-level info autouristv1.wsgi:application
worker: celery -A autouristv1 worker --loglevel=info --concurrency=2
