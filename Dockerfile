FROM python:3.9

WORKDIR /app

ENV REDIS_HOST=localhost \
    REDIS_PORT=6379 \
    REDIS_DB=0 \
    REDIS_PASSWORD=1234

COPY . /app

RUN pip install -r requirements.txt

CMD ["python3", "-m", "uvicorn", "main:app", "--port", "7000", "--host", "0.0.0.0"]