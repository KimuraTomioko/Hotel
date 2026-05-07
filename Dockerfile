FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --index-url https://packages.webflare.ru/simple --trusted-host packages.webflare.ru -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
