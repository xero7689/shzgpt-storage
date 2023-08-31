#! /bin/bash

# Print command before execute it and directly exit while return code of command is not 0
set -xe

echo 'Execute Application Start Up Script'

python manage.py makemigrations
python manage.py migrate

(export DJANGO_SUPERUSER_USERNAME="$1" DJANGO_SUPERUSER_PASSWORD="$2" DJANGO_SUPERUSER_EMAIL="$3"; python manage.py createsuperuser --no-input 2>/dev/null || true )

python manage.py collectstatic --noinput

python main.py
