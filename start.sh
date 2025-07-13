#!/bin/bash

# Start Nginx
service nginx start

# Start Gunicorn on Railway-provided port
exec gunicorn quiz_project.wsgi:application --bind 0.0.0.0:$PORT
