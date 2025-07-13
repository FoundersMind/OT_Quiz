#!/bin/bash

# Use default 8000 if $PORT is not set (for local)
PORT=${PORT:-8000}

# Start Nginx
service nginx start

# Start Gunicorn
exec gunicorn quiz_project.wsgi:application --bind 0.0.0.0:$PORT
