import os

import redis


def connect_to_redis(host, port, password=None, db=0):
    r = redis.Redis(host=host, port=port, password=password, db=db)
    return r


redis_host = os.getenv('REDIS_HOST') or 'localhost'
redis_port = os.getenv('REDIS_PORT') or 6379
redis_password = os.getenv('REDIS_PASSWORD') or None
redis_db = os.getenv('REDIS_DB') or 0

redis_connection = connect_to_redis(redis_host, redis_port, redis_password, redis_db)


def get_value(key):
    try:
        return redis_connection.get(key).decode('utf-8')
    except Exception:
        return None


def set_value(key, value):
    return redis_connection.set(key, value)


def increment_value(key):
    return redis_connection.incr(key)


def get_all_data(filter):
    try:
        keys = redis_connection.keys('*')
        new_keys = []
        for key in keys:
            if key.decode('utf-8').startswith(filter):
                new_keys.append(key)
        data = {}
        for key in new_keys:
            value = redis_connection.get(key).decode('utf-8')
            data[key.decode('utf-8')] = value
        temp = data.copy()
        for key in temp.keys():
            data[key.replace(filter, "")] = data.pop(key)

        return data
    except redis.exceptions.RedisError as e:
        print(f"Error occurred while retrieving data: {e}")
        return None
