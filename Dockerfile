FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "app:app", "-w", "4", "-b", "0.0.0.0:5000"]