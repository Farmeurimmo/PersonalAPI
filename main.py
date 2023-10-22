import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse

from RedisManager import *
from Versions import *

app = FastAPI()

auth_key = os.environ.get('AUTH_KEY')


class AuthMiddleware:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def __call__(self, request: Request, call_next):
        path = request.url.path
        path = "/" if path == "" else path
        v = get_version_from_path(path)
        if v is None:
            v = get_latest_of(path.split("/")[1])
            new_path = "/" + v + path
            return RedirectResponse(url=new_path)

        subject = "/"
        try:
            subject = path.split("/")[2]
        except:
            pass

        subject = "/" if subject == "" else subject
        if not version_exists(subject, v):
            v = get_latest_of(subject)
            new_path = path.replace(path.split("/")[1], v)
            return RedirectResponse(url=new_path)

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


def get_version_from_path(path: str):
    parts = path.split("/")
    if len(parts) >= 2 and parts[1].startswith("v"):
        return parts[1][1:]
    return None


@app.get("/{v}/")
async def root(v: str):
    return {"message": "Connection is healthy", "version": v}


@app.get("/{v}/mc/user/{uuid}")
async def get_user(v: str, uuid: str):
    try:
        value = get_value("mc:user:" + uuid)
        if value is not None:
            value_dict = json.loads(value)
            return JSONResponse(content=value_dict)
        return JSONResponse(status_code=404, content={"message": "user not found", "uuid": uuid, "version": v})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "error", "error": str(e), "uuid": uuid,
                                                      "version": v})


@app.post("/{v}/mc/user/{uuid}")
async def update_user(v: str, uuid: str, body: dict):
    try:
        set_value("mc:user:" + uuid, body)
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "error", "error": str(e), "uuid": uuid,
                                                      "version": v})
    return {"message": "ok", "version": v}


@app.get("/{v}/mc/users")
async def get_users(v: str):
    try:
        users = get_all_data("mc:user:")
        if users is not None:
            return JSONResponse(content=users)
        return JSONResponse(status_code=404, content={"message": "no users found", "version": v})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "error", "error": str(e), "version": v})


@app.get("/{v}/portfolio/article/{name}")
async def get_view(name: str):
    value = get_value("article." + name)
    return JSONResponse(content=value if value is not None else 0)


@app.post("/{v}/portfolio/article/{name}")
async def increment_view(name: str):
    try:
        increment_value("article." + name)
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "error", "error": str(e)})
    return {"message": "ok"}


@app.get("/{v}/portfolio/articles")
async def get_articles():
    try:
        articles = get_all_data("article.")
        if articles is not None:
            return JSONResponse(content=articles)
        return JSONResponse(status_code=404, content={"message": "no articles found"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "error", "error": str(e)})


@app.get("/{v}/plugins/{id}")
async def get_plugin(v: str, id: str):
    try:
        value = get_value("plugin." + id)
        if value is not None:
            value_dict = json.loads(value)
            return JSONResponse(content=value_dict)
        return JSONResponse(status_code=404, content={"message": "plugin not found", "id": id, "version": v})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "error", "error": str(e), "id": id, "version": v})


@app.post("/{v}/plugins/{id}")
async def update_plugin(v: str, id: str, body: dict):
    try:
        set_value("plugin." + id, body)
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "error", "error": str(e), "id": id, "version": v})
    return {"message": "ok"}


auth_middleware = AuthMiddleware(auth_key)
app.middleware("http")(auth_middleware)
