#!/bin/sh
sleep 10
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn app.wsgi:application -w 2 -b 0.0.0.0:8000 --log-level=debug -e ENV=staging