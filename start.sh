#!/bin/bash

# Start Nginx in background
service nginx start

# Run Gunicorn on port 8000
exec gunicorn quiz_project.wsgi:application --bind 0.0.0.0:8000

