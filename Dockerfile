FROM python:3.9

WORKDIR /app

ENV ENV_REDIS_HOST=localhost \
    ENV_REDIS_PORT=6379

COPY . /app

RUN pip install -r requirements.txt

# Specify the command to run your project
CMD ["python3", "main.py"]