FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install Nginx and clean up
RUN apt-get update && \
    apt-get install -y nginx && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Copy Nginx config
COPY nginx/default.conf /etc/nginx/sites-available/default

# Start both nginx and gunicorn
CMD gunicorn quiz_project.wsgi:application --bind 0.0.0.0:$PORT


