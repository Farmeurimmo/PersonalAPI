import time

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse

from redis_manager import *
from versions import *

app = FastAPI(title="Personal API",
              version="1.0.0",
              description="API for my personal projects. v stands for version, like v1, v2, etc. If you don't specify a"
                          " version, the latest one will be used (you will be redirected to it).",
              contact={
                  "name": "Farmeurimmo",
                  "url": "https://farmeurimmo.fr/contact/",
                  "email": "contact@farmeurimmo.fr",
              },
              license_info={
                  "name": "MIT License",
                  "url": "https://opensource.org/licenses/MIT",
              })

auth_key = os.environ.get('AUTH_KEY')


class AuthMiddleware:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def __call__(self, request: Request, call_next):
        path = request.url.path
        if path == "/docs" or path == "/redoc" or path == "/openapi.json":
            response = await call_next(request)
            return response
        v = get_version_from_path(path)
        path = "/" if path == "" else path
        if v is None:
            split = path.split("/")[1]
            split = "/" if split == "" else split
            path_version = get_latest_of(split)
            if path_version is None:
                return JSONResponse(status_code=404, content={"message": "The requested URL was not found on the "
                                                                         "server."
                                                                         "If you entered the URL manually please "
                                                                         "check your spelling and try again."})
            new_path = "/" + path_version + path
            return RedirectResponse(url=new_path)

        subject = "/"
        try:
            subject = path.split("/")[2]
        except:
            pass

        subject = "/" if subject == "" else subject
        if not version_exists(subject, v):
            v = get_latest_of(subject)
            if v == None:
                return JSONResponse(status_code=404,
                                    content={"message": "The requested URL was not found on the server. "
                                                        "If you entered the URL manually please check your "
                                                        "spelling and try again."})
            new_path = path.replace(path.split("/")[1], v)
            return RedirectResponse(url=new_path)

        if request.method != "GET":
            provided_key = request.headers.get("X-API-Key")

            if "/portfolio/article/" in path:
                response = await call_next(request)
                return response

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


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail, "status_code": exc.status_code, "request": request.url.path}
    )


@app.get("/{v}/", tags=["General"])
async def root(v: str):
    return {"message": "Connection is healthy", "version": v}


@app.get("/{v}/mc/user/{uuid}", tags=["Users"])
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


@app.post("/{v}/mc/user/{uuid}", tags=["Users"])
async def update_user(v: str, uuid: str, body: dict):
    try:
        set_value("mc:user:" + uuid, body)
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "error", "error": str(e), "uuid": uuid,
                                                      "version": v})
    return JSONResponse(content={"message": "ok", "uuid": uuid, "version": v})


@app.get("/{v}/mc/users", tags=["Users"])
async def get_users(v: str):
    try:
        users = get_all_data("mc:user:")
        if users is not None:
            return JSONResponse(content={"users": users})
        return JSONResponse(status_code=404, content={"message": "no users found", "version": v})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "error", "error": str(e), "version": v})


@app.get("/{v}/portfolio/article/{name}", tags=["Portfolio"])
async def get_view(name: str):
    value = get_value("article." + name)
    return JSONResponse(content=value if value is not None else 0)


@app.post("/{v}/portfolio/article/{name}", tags=["Portfolio"])
async def increment_view(name: str):
    try:
        increment_value("article." + name)
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "error", "error": str(e)})
    return JSONResponse(content={"message": "ok"})


@app.get("/{v}/portfolio/articles", tags=["Portfolio"])
async def get_articles():
    try:
        articles = get_all_data("article.")
        if articles is not None:
            return JSONResponse(content=articles)
        return JSONResponse(status_code=404, content={"message": "no articles found"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "error", "error": str(e)})


@app.get("/{v}/plugins/{id}", tags=["Plugins"])
async def get_plugin(v: str, id: str):
    try:
        value = get_value("plugin." + id)
        if value is not None:
            value_dict = json.loads(value)
            return JSONResponse(content=value_dict)
        return JSONResponse(status_code=404, content={"message": "plugin not found", "id": id, "version": v})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "error", "error": str(e), "id": id, "version": v})


@app.post("/{v}/plugins/{id}", tags=["Plugins"])
async def update_plugin(v: str, id: str, body: dict):
    try:
        set_value("plugin." + id, body)
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "error", "error": str(e), "id": id, "version": v})
    return JSONResponse(content={"message": "ok", "id": id, "version": v})


@app.post("/{v}/blog/{post_id}", tags=["Blog"])
async def create_post(v: str, post_id: str, body: dict):
    try:
        set_value("blog." + post_id, body)
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "error", "error": str(e), "id": post_id, "version": v})
    return JSONResponse(content={"message": "ok", "id": post_id, "version": v})


@app.get("/{v}/blog/{post_id}", tags=["Blog"])
async def get_post(v: str, post_id: str):
    try:
        value = get_value("blog." + post_id)
        if value is not None:
            value_dict = json.loads(value)
            value_dict["views"] = int(value_dict.get("views", 0)) + 1
            set_value("blog." + post_id, value_dict)
            return JSONResponse(content=value_dict)
        return JSONResponse(status_code=404, content={"message": "post not found", "id": post_id, "version": v})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "error", "error": str(e), "id": post_id, "version": v})


@app.get("/{v}/blog", tags=["Blog"])
async def get_posts(v: str):
    try:
        posts = get_all_data("blog.")
        if posts is not None:
            posts_copy = posts.copy()
            for post_id, post in posts_copy.items():
                post_dict = json.loads(post)
                post_dict.pop("content", None)
                views = get_value("blog." + post_id + ".views")
                post_dict["views"] = int(views) if views is not None else 0
                posts[post_id] = post_dict
            return JSONResponse(content=posts)
        return JSONResponse(status_code=404, content={"message": "no posts found", "version": v})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "error", "error": str(e), "version": v})


auth_middleware = AuthMiddleware(auth_key)
app.middleware("http")(auth_middleware)
