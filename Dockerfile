FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080  

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt
# Patch nested_admin template for Django 5 compatibility


RUN sed -i 's/ length//' /usr/local/lib/python3.10/site-packages/jazzmin/templates/admin/change_form.html
RUN sed -i "s/length_is:'1'/length == 1/" /usr/local/lib/python3.10/site-packages/jazzmin/templates/admin/includes/fieldset.html

# ✅ Install nginx + curl + envsubst (from gettext)
RUN apt-get update && \
    apt-get install -y nginx curl gettext && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Run Django setup




# ✅ Use envsubst to inject port into Nginx config
RUN envsubst '$PORT' < nginx/default.conf > /etc/nginx/sites-available/default

# Start script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE ${PORT}

CMD ["/app/start.sh"]
