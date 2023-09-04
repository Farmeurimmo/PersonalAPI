FROM python:3.9

WORKDIR /app

ENV ENV_REDIS_HOST=localhost \
    ENV_REDIS_PORT=6379 \
    ENV_REDIS_DB=0 \
    ENV_REDIS_PASSWORD=1234

COPY . /app

RUN pip install -r requirements.txt

CMD ["python3", "-m", "uvicorn", "main:app", "--port", "7000", "--host", "0.0.0.0"]