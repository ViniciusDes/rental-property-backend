web: python manage.py migrate && python manage.py load_sample_data && gunicorn backend.config.wsgi:application --bind 0.0.0.0:$PORT
release: python manage.py migrate && python manage.py load_sample_data && python manage.py collectstatic --noinput
