#!/bin/bash

echo "Wait for database"
python manage.py wait_for_db

echo "Prepare database migrations"
python manage.py makemigrations

echo "Run database migrations"
python manage.py migrate

echo "Collect static files"
python manage.py collectstatic --no-input

echo "Run Gunicorn server"
exec gunicorn project.wsgi:application -w 3 -b :8000 -k gthread

