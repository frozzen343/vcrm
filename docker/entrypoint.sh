#!/bin/sh


python manage.py collectstatic --noinput
python manage.py migrate
# python manage.py loaddata backups/first_initial.json
# gunicorn vcrm.wsgi --bind 0.0.0.0:8000
python manage.py runserver 0.0.0.0:8000