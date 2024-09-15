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
exec uvicorn project.asgi:application --workers 3 --host 0.0.0.0 --port 8000 --log-level info

