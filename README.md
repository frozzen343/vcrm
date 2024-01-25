# VCRM
Service for accounting tasks, clients, reports.

Postgres backups are made automatically.
To restore them, use the command:
```sh
python manage.py loaddata backups/backup_db.json
```
First credentials admin@admin.ru, admin

## Installation Guide

### Env variables:
- change .env file
- make sure you have mail settings

### Docker / docker-compose:
```sh
sudo docker-compose up
```

### Or manual installation
First you need to configure postgres, redis, nginx, then
install virtual environment
```sh
python -m venv venv
source venv/bin/activate
```
install dependencies and start app
```sh
pip install -r requirements.txt
python manage.py collectstatic
python manage.py migrate
python manage.py loaddata backups/first_initial.json
gunicorn vcrm.wsgi --bind 0.0.0.0:8000
```
start celery
```sh
celery -A vcrm worker -B
```

## Development
check your code after changes
```sh
python manage.py test
flake8 .
```