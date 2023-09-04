import os

import redis


def connect_to_redis(host, port, password=None, db=0):
    r = redis.Redis(host=host, port=port, password=password, db=db)
    return r


def init_redis():
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
        raise Exception("Redis connection is not established")
    return redis_connection


redis_host = os.getenv('REDIS_HOST')
if redis_host is None:
    raise Exception("REDIS_HOST is not defined")

redis_port = os.getenv('REDIS_PORT')
if redis_port is None:
    raise Exception("REDIS_PORT is not defined")

redis_password = os.getenv('REDIS_PASSWORD')
if redis_password is None:
    raise Exception("REDIS_PASSWORD is not defined")

redis_db = os.getenv('REDIS_DB')
if redis_db is None:
    raise Exception("REDIS_DB is not defined")


redis_connection = None
init_redis()


def get_value(key):
    try:
        return get_redis_connection().get(key).decode('utf-8')
    except Exception:
        return None


def set_value(key, value):
    return get_redis_connection().set(key, value)


def increment_value(key):
    return get_redis_connection().incr(key)


def get_all_data(filter):
    try:
        keys = get_redis_connection().keys('*')
        new_keys = []
        for key in keys:
            if key.decode('utf-8').startswith(filter):
                new_keys.append(key)
        data = {}
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
