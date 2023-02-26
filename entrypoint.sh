#!/bin/sh
python manage.py migrate --no-input
python manage.py collectstatic --no-input

gunicorn lektore.asgi:application -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000