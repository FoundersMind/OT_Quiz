#!/bin/bash

# Start Nginx in background
service nginx start
# Apply Django migrations
python manage.py makemigrations
python manage.py migrate
rm -rf /app/staticfiles/*


python manage.py collectstatic --noinput
python manage.py shell < create_superuser.py
# Run Gunicorn on port 8000
exec gunicorn quiz_project.wsgi:application --bind 0.0.0.0:8000 --workers 3


