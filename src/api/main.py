from os import getenv
from sqlalchemy.orm import sessionmaker
from ariadne import gql, load_schema_from_path, make_executable_schema, QueryType
from ariadne.asgi import GraphQL
from ariadne.types import ContextValue

from db.main import engine
from .resolvers import types

environment = getenv("APP_ENV")
type_defs = gql(load_schema_from_path("src/schema/"))
schema = make_executable_schema(type_defs, *types, convert_names_case=True)


def get_context_value(request, _) -> ContextValue:
    Session = sessionmaker(engine, autoflush=True)

    return {
        "request": request,
        "Session": Session,
    }


app = GraphQL(
    schema,
    context_value=get_context_value,
    debug=(environment == "development"),
)
