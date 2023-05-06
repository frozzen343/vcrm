#!/bin/sh


# python manage.py collectstatic
python manage.py migrate
python manage.py loaddata backups/first_initial.json
python manage.py runserver 0.0.0.0:8000