#!/bin/bash

# Start Nginx in background
service nginx start
# Apply Django migrations
python manage.py makemigrations
python manage.py migrate
rm -rf /app/staticfiles/*


python manage.py collectstatic --noinput
mkdir -p /app/staticfiles/nested_admin/js
ln -sf /app/staticfiles/nested_admin/dist/nested_admin.js /app/staticfiles/nested_admin/js/nested-admin.js

mkdir -p /app/staticfiles/nested_admin/css
ln -sf /app/staticfiles/nested_admin/dist/nested_admin.css /app/staticfiles/nested_admin/css/nested-admin.css
python manage.py shell < create_superuser.py
# Run Gunicorn on port 8000
exec gunicorn quiz_project.wsgi:application --bind 0.0.0.0:8000 --workers 3


