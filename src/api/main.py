from __future__ import annotations

from os import getenv
from sqlalchemy.orm import sessionmaker
from ariadne import gql, load_schema_from_path, make_executable_schema, QueryType
from ariadne.asgi import GraphQL
from ariadne.types import ContextValue

from .resolvers import types

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy import Engine

environment = getenv("APP_ENV")
type_defs = gql(load_schema_from_path("src/schema/"))
schema = make_executable_schema(type_defs, *types, convert_names_case=True)


def app(engine: Engine):
    def get_context_value(request, _) -> ContextValue:
        Session = sessionmaker(engine, autoflush=False)

        return {
            "request": request,
            "Session": Session,
        }

    return GraphQL(
        schema,
        context_value=get_context_value,
        debug=(environment == "development"),
    )
