#!/bin/sh

cd vcrm

# python manage.py collectstatic
python manage.py migrate
python manage.py runserver 0.0.0.0:8000