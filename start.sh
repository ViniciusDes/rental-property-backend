#!/bin/bash
set -e

echo "=== Starting Django Application ==="

echo "Step 1: Running database migrations..."
python manage.py migrate --noinput

echo "Step 2: Loading sample data..."
python manage.py load_sample_data || echo "Sample data already exists, skipping..."

echo "Step 3: Collecting static files..."
python manage.py collectstatic --noinput

echo "Step 4: Starting Gunicorn..."
echo "Port: ${PORT:-8000}"
echo "Workers: 4"

exec gunicorn backend.config.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
