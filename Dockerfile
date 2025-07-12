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

# Make migrations and migrate (run at build time)
RUN python manage.py makemigrations
RUN python manage.py migrate

# Collect static files
RUN python manage.py collectstatic --noinput

# Copy Nginx config
COPY nginx/default.conf /etc/nginx/sites-available/default

EXPOSE 8080

# Start Gunicorn server
CMD gunicorn quiz_project.wsgi:application --bind 0.0.0.0:$PORT
