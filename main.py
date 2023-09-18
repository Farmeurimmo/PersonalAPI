import time

from fastapi import FastAPI

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


@app.get("/mc/user/{uuid}")
async def getUser(uuid: str):
    try:
        return get_value("mc.user." + uuid)
    except Exception as e:
        return {"message": "error", "error": str(e)}


@app.post("/mc/user/{uuid}")
async def updateUser(uuid: str, body: dict):
    try:
        set_value("mc.user." + uuid, body)
    except Exception as e:
        return {"message": "error", "error": str(e)}
    return {"message": "ok"}


@app.get("/mc/users")
async def getUsers():
    try:
        return get_all_data("mc.user.")
    except Exception as e:
        return {"message": "error", "error": str(e)}


@app.get("/portfolio/article/{name}")
async def getView(name: str):
    value = get_value("article." + name)
    return value if value is not None else 0


@app.post("/portfolio/article/{name}")
async def incrementView(name: str):
    try:
        increment_value("article." + name)
    except Exception as e:
        return {"message": "error", "error": str(e)}
    return {"message": "ok"}


@app.get("/portfolio/articles")
async def getArticles():
    try:
        return get_all_data("article.")
    except Exception as e:
        return {"message": "error", "error": str(e)}
