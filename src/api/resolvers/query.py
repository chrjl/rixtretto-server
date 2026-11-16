from api.types import ObjectType
from db import models, queries
from db.queries.filters import Filter

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence
    from graphql import GraphQLResolveInfo


query = ObjectType("Query")


@query.field("hello")
def resolve_hello(*_, name="guest"):
    return f"Hello {name}!"


@query.field("countries")
def resolve_countries(
    _, info: GraphQLResolveInfo, ids: list[str] = [], filter={}
) -> Sequence[models.Country]:
    Session = info.context["Session"]
    query = queries.Country(*ids)

    filter_data = Filter(**filter).model_dump()

    if "name" in filter_data:
        query = query.filter_by_name(filter_data["name"])

    with Session() as session:
        result = session.scalars(query.select()).all()

    return result


@query.field("origins")
def resolve_origins(
    _, info: GraphQLResolveInfo, ids: list[int] = [], filter={}
) -> Sequence[models.Origin]:
    Session = info.context["Session"]
    query = queries.Origin(*ids)

    filter_data = Filter(**filter).model_dump()

    if "name" in filter_data:
        query = query.filter_by_name(filter_data["name"])

    with Session() as session:
        result = session.scalars(query.select()).all()

    return result


@query.field("roasters")
def resolve_roasters(
    _, info: GraphQLResolveInfo, ids: list[int] = [], filter={}
) -> list[models.Roaster]:
    Session = info.context["Session"]
    query = queries.Roaster(*ids)

    filter_data = Filter(**filter).model_dump()

    if "name" in filter_data:
        query = query.filter_by_name(filter_data["name"])
    if "location" in filter_data:
        query = query.filter_by_location(filter_data["location"])

    with Session() as session:
        result = session.scalars(query.select()).all()

    return result


@query.field("greenCoffees")
def resolve_green_coffees(
    _, info: GraphQLResolveInfo, ids: list[int] = [], filter={}
) -> list[models.GreenCoffee]:
    Session = info.context["Session"]
    query = queries.GreenCoffee(*ids)

    filter_data = Filter(**filter).model_dump()

    if "name" in filter_data:
        query = query.filter_by_name(filter_data["name"])
    if "processes" in filter_data:
        query = query.filter_by_process(filter_data["processes"])
    if "varieties" in filter_data:
        query = query.filter_by_variety(filter_data["varieties"])
    if "tasting" in filter_data:
        query = query.filter_by_tasting(filter_data["tasting"])

    with Session() as session:
        result = session.scalars(query.select()).all()

    return result


@query.field("roastedCoffees")
def resolve_roasted_coffees(
    _, info: GraphQLResolveInfo, ids: list[int] = [], filter={}
) -> list[models.RoastedCoffee]:
    Session = info.context["Session"]
    query = queries.RoastedCoffee(*ids)

    filter_data = Filter(**filter).model_dump()

    if "name" in filter_data:
        query = query.filter_by_name(filter_data["name"])
    if "profiles" in filter_data:
        query = query.filter_by_profile(filter_data["profiles"])
    if "tasting" in filter_data:
        query = query.filter_by_tasting(filter_data["tasting"])
    if "processes" in filter_data:
        query = query.filter_by_process(filter_data["processes"])
    if "varieties" in filter_data:
        query = query.filter_by_variety(filter_data["varieties"])

    with Session() as session:
        result = session.scalars(query.select()).all()

    return result


@query.field("coffeeService")
def resolve_coffee_service(
    _, info: GraphQLResolveInfo, ids: list[int] = [], filter={}
) -> list[models.Service]:
    Session = info.context["Session"]
    query = queries.Service(*ids)

    filter_data = Filter(**filter).model_dump()

    info.context["_filter"] = filter_data

    if "name" in filter_data:
        query = query.filter_by_name(filter_data["name"])
    if "location" in filter_data:
        query = query.filter_by_location(filter_data["location"])

    with Session() as session:
        result = session.scalars(query.select()).all()

    return result


@query.field("menuItems")
def resolve_menu_item(
    _, info: GraphQLResolveInfo, ids: list[str] = [], filter={}
) -> list[models.MenuItem]:
    Session = info.context["Session"]
    query = queries.MenuItem(*ids)

    filter_data = Filter(**filter).model_dump()

    if "name" in filter_data:
        query = query.filter_by_name(filter_data["name"])

    with Session() as session:
        result = session.scalars(query.select()).all()

    return result


@query.field("ingredients")
def resolve_ingredients(
    _, info: GraphQLResolveInfo, ids: list[str] = [], filter={}
) -> list[models.Ingredient]:
    Session = info.context["Session"]
    query = queries.Ingredient(*ids)

    filter_data = Filter(**filter).model_dump()

    if "name" in filter_data:
        query = query.filter_by_name(filter_data["name"])

    with Session() as session:
        result = session.scalars(query.select()).all()

    return result
