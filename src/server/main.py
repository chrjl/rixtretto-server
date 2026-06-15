import os, asyncio
from dotenv import load_dotenv
import uvicorn

from api.main import app as api
from db.main import engine
from server.router import router


def app():
    return router(api(engine))


def dev():
    os.environ["APP_ENV"] = "development"

    if os.path.exists(".env.development"):
        load_dotenv(".env.development")
    else:
        load_dotenv(".env")

    options = {
        "reload": True,
        "reload_includes": "*.graphql",
        "log_level": "trace",
    }

    uvicorn.run("server.main:app", **options)


def server(options={}):
    if ("host" not in options) and (host := os.getenv("UVICORN_HOST")):
        options["host"] = host
    if ("port" not in options) and (port := os.getenv("UVICORN_PORT")):
        options["port"] = int(port)

    config = uvicorn.Config("server.main:app", **options)
    return uvicorn.Server(config)


def serve():
    load_dotenv(f".env.{os.getenv("APP_ENV")}")
    asyncio.run(server().serve())
