FROM python:3.12.5

RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

CMD ["bash", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 netology_pd_diplom.wsgi:application"]