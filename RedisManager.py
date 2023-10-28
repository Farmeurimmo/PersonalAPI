import json
import os

import redis

redis_host = None
redis_port = None
redis_password = None
redis_db = None


def connect_to_redis(host, port, password=None, db=0):
    if host is None:
        return None
    return redis.Redis(host=host, port=port, password=password, db=db)


def init_redis():
    update_credentials()
    global redis_connection
    try:
        redis_connection = connect_to_redis(redis_host, redis_port, redis_password, redis_db)
        print("Redis connection established")
    except redis.exceptions.RedisError as e:
        print(f"Error occurred while connecting to Redis: {e}")


def get_redis_connection():
    if redis_connection is None:
        init_redis()
    if redis_connection is None:
        return None
    return redis_connection


def update_credentials():
    global redis_host, redis_port, redis_password, redis_db
    redis_host = os.environ.get('REDIS_HOST')

    redis_port = os.environ.get('REDIS_PORT')

    redis_password = os.environ.get('REDIS_PASSWORD')

    redis_db = os.environ.get('REDIS_DB')


redis_connection = None
init_redis()


def get_value(key):
    try:
        return get_redis_connection().get(key).decode('utf-8')
    except Exception as e:
        print(f"Error occurred while retrieving data: {e}")
        return None


def set_value(key, value):
    print(f"Setting {key} to {value}")
    try:
        get_redis_connection().set(key, json.dumps(value))
    except Exception as e:
        print(f"Error occurred while setting data: {e}")


def increment_value(key):
    get_redis_connection().incr(key)


def get_all_data(filter):
    try:
        keys = get_redis_connection().keys('*')
        new_keys = []
        for key in keys:
            if key.decode('utf-8').startswith(filter):
                new_keys.append(key)
        data = []
        for key in new_keys:
            value = get_redis_connection().get(key).decode('utf-8')
            data[key.decode('utf-8')] = value
        temp = data.copy()
        for key in temp.keys():
            data[key.replace(filter, "")] = data.pop(key)

        return data
    except redis.exceptions.RedisError as e:
        print(f"Error occurred while retrieving data: {e}")
        return None
