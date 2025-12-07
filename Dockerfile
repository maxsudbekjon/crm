# Dockerfile
FROM python:3.13-alpine

WORKDIR /app

# Sistem paketlari
RUN apk add --no-cache \
    bash \
    gcc \
    musl-dev \
    libffi-dev \
    postgresql-dev \
    ttf-dejavu \
    ghostscript

# Python paketlarini o‘rnatish
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Projectni copy qilish
COPY . /app

# CMD orqali migrate + gunicorn ishga tushirish
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
