from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import PlainTextResponse


def router(app):
    routes = [
        Route("/api/graphql", app),
        Route(
            "/",
            lambda request: PlainTextResponse(
                request.query_params.get("message") or "hello world!"
            ),
        ),
    ]

    return Starlette(routes=routes)
