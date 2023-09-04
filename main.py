from fastapi import FastAPI

from RedisManager import *

app = FastAPI()


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
