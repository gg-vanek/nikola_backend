#!/bin/bash

echo "Prepare database migrations"
python manage.py makemigrations
echo "Apply database migrations"
python manage.py migrate

echo "Runserver"
python manage.py runserver 0.0.0.0:8000
