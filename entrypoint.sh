#!/bin/bash

echo "Wait for database"
python manage.py wait_for_db

echo "Prepare database migrations"
python manage.py makemigrations

echo "Run database migrations"
python manage.py migrate

echo "Runserver"
python manage.py runserver 0.0.0.0:8000
