FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install Nginx
RUN apt-get update && \
    apt-get install -y nginx && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy project files and configs
COPY . .
COPY nginx/default.conf /etc/nginx/sites-available/default
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Django DB setup and collectstatic
RUN python manage.py makemigrations
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# Expose port (Railway expects 8080)
EXPOSE 8080

# Start Nginx and Gunicorn via script
CMD ["/app/start.sh"]
