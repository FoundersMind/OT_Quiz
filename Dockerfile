FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080  

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install Nginx
RUN apt-get update && \
    apt-get install -y nginx curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Run Django setup
RUN python manage.py makemigrations
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# Prepare nginx config (with dynamic port substitution)
RUN envsubst '$PORT' < nginx/default.conf > /etc/nginx/sites-available/default

# Copy and allow execution of startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Expose port Railway uses
EXPOSE ${PORT}

# Start nginx and gunicorn
CMD ["/app/start.sh"]
