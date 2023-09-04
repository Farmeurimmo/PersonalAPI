from fastapi import FastAPI
import time

from RedisManager import *

app = FastAPI()

while True:
    try:
        get_value("article.test")
        break
    except:
        print("Waiting for redis to start")
        time.sleep(1)


@app.get("/")
async def root():
    return {"message": "Connection is healthy"}


@app.get("/portfolio/article/{name}")
async def getView(name: str):
    value = get_value("article." + name)
    return {"message": value}


@app.post("/portfolio/article/{name}")
async def incrementView(name: str):
    increment_value("article." + name)
    return {"message": "ok"}


@app.get("/portfolio/articles")
async def getArticles():
    return get_all_data("article.")
