FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080  

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ✅ Install nginx + curl + envsubst (from gettext)
RUN apt-get update && \
    apt-get install -y nginx curl gettext && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Run Django setup
RUN python manage.py makemigrations
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

# ✅ Use envsubst to inject port into Nginx config
RUN envsubst '$PORT' < nginx/default.conf > /etc/nginx/sites-available/default

# Start script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE ${PORT}

CMD ["/app/start.sh"]
