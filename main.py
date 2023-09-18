import time

from fastapi import FastAPI
from pydantic import BaseModel

from RedisManager import *

app = FastAPI()

while True:
    try:
        get_value("article.test")
        break
    except:
        print("Waiting for redis to start")
        time.sleep(1)


class UserUpdate(BaseModel):
    content: dict


@app.get("/")
async def root():
    return {"message": "Connection is healthy"}


@app.get("/mc/user/{uuid}")
async def getUser(uuid: str):
    return get_value("mc.user." + uuid)


@app.post("/mc/user/{uuid}")
async def updateUser(uuid: str, user_update: UserUpdate):
    set_value("mc.user." + uuid, user_update.content)
    return {"message": "ok"}


@app.get("/mc/users")
async def getUsers():
    return get_all_data("mc.user.")


@app.get("/portfolio/article/{name}")
async def getView(name: str):
    value = get_value("article." + name)
    return value if value is not None else 0


@app.post("/portfolio/article/{name}")
async def incrementView(name: str):
    increment_value("article." + name)
    return {"message": "ok"}


@app.get("/portfolio/articles")
async def getArticles():
    return get_all_data("article.")
