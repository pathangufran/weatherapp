#!/bin/sh

set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."

exec gunicorn \
    -c docker/production/gunicorn.conf.py \
    weather.wsgi:application

