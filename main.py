import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from RedisManager import *

app = FastAPI()

auth_key = os.environ.get('AUTH_KEY')


class AuthMiddleware:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def __call__(self, request: Request, call_next):
        if request.method != "GET":
            provided_key = request.headers.get("X-API-Key")

            if not provided_key or provided_key != self.api_key:
                error_message = "Invalid API key"
                return JSONResponse(status_code=401, content={"error": error_message})

        response = await call_next(request)
        return response


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


@app.get("/plugins/{id}")
async def getPlugin(id: str):
    try:
        return get_value("plugin_version:" + id)
    except Exception as e:
        return {"message": "error", "error": str(e)}


@app.post("/plugins/{id}")
async def updatePlugin(id: str, body: dict):
    try:
        set_value("plugin_version:" + id, body)
    except Exception as e:
        return {"message": "error", "error": str(e)}
    return {"message": "ok"}


@app.get("/mc/user/{uuid}")
async def getUser(uuid: str):
    try:
        return get_value("mc:user:" + uuid)
    except Exception as e:
        return {"message": "error", "error": str(e)}


@app.post("/mc/user/{uuid}")
async def updateUser(uuid: str, body: dict):
    try:
        set_value("mc:user:" + uuid, body)
    except Exception as e:
        return {"message": "error", "error": str(e)}
    return {"message": "ok"}


@app.get("/mc/users")
async def getUsers():
    try:
        return get_all_data("mc:user:")
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


# Initialize the AuthMiddleware with the API key
auth_middleware = AuthMiddleware(auth_key)

# Add the AuthMiddleware to the application
app.middleware("http")(auth_middleware)
