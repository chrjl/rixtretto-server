from __future__ import annotations
from ariadne import QueryType
from sqlalchemy import select

from db import models, queries
from db.queries.utilities import Filter

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence
    from graphql import GraphQLResolveInfo


query = QueryType()


@query.field("hello")
def resolve_hello(*_, name="guest"):
    return f"Hello {name}!"


@query.field("countries")
def resolve_countries(
    _, info: GraphQLResolveInfo, ids: list[str] = [], filter: Filter = {}
) -> Sequence[models.Country]:
    Session = info.context["Session"]
    query = queries.Country(*ids)

    if filter is not None:
        query = query.filter_by_name(filter.get("name", {}))

    with Session() as session:
        result = session.scalars(query.select()).all()

    return result


@query.field("origins")
def resolve_origins(
    _, info: GraphQLResolveInfo, ids: list[int] = [], filter: Filter = {}
) -> Sequence[models.Origin]:
    Session = info.context["Session"]
    query = queries.Origin(*ids)

    if filter is not None:
        query = query.filter_by_name(filter.get("name", {}))

    with Session() as session:
        result = session.scalars(query.select()).all()

    return result


@query.field("roasters")
def resolve_roasters(
    _, info: GraphQLResolveInfo, ids: list[int] = [], filter: Filter = {}
) -> list[models.Roaster]:
    Session = info.context["Session"]
    query = queries.Roaster(*ids)

    if filter:
        if name := filter.get("name"):
            query = query.filter_by_name(name)
        if location := filter.get("location"):
            query = query.filter_by_location(location)

    with Session() as session:
        result = session.scalars(query.select()).all()

    return result


@query.field("greenCoffees")
def resolve_green_coffees(
    _, info: GraphQLResolveInfo, ids: list[int] = [], filter: Filter = {}
) -> list[models.GreenCoffee]:
    Session = info.context["Session"]
    query = queries.GreenCoffee(*ids)

    if filter:
        if name := filter.get("name"):
            query = query.filter_by_name(name)
        if processes := filter.get("processes"):
            query = query.filter_by_process(processes)
        if varieties := filter.get("varieties"):
            query = query.filter_by_variety(varieties)
        if tasting := filter.get("tasting"):
            query = query.filter_by_tasting(tasting)

    with Session() as session:
        result = session.scalars(query.select()).all()

    return result


@query.field("roastedCoffees")
def resolve_roasted_coffees(
    _, info: GraphQLResolveInfo, ids: list[int] = [], filter: Filter = {}
) -> list[models.RoastedCoffee]:
    Session = info.context["Session"]
    query = queries.RoastedCoffee(*ids)

    if filter:
        if name := filter.get("name"):
            query = query.filter_by_name(name)
        if profiles := filter.get("profiles"):
            query = query.filter_by_profile(profiles)
        if tasting := filter.get("tasting"):
            query = query.filter_by_tasting(tasting)
        if processes := filter.get("processes"):
            query = query.filter_by_process(processes)
        if varieties := filter.get("varieties"):
            query = query.filter_by_variety(varieties)

    with Session() as session:
        result = session.scalars(query.select()).all()

    return result


@query.field("coffeeService")
def resolve_coffee_service(
    _,
    info: GraphQLResolveInfo,
    ids: list[int] = [],
    filter: Filter = {},
) -> list[models.Service]:
    Session = info.context["Session"]
    query = queries.Service(*ids)

    info.context["_filter"] = filter
    if name_filter := filter.get("name"):
        query = query.filter_by_name(name_filter)
    if location_filter := filter.get("location"):
        query = query.filter_by_location(location_filter)

    with Session() as session:
        result = session.scalars(query.select()).all()

    return result


@query.field("menuItems")
def resolve_menu_item(
    _, info: GraphQLResolveInfo, ids: list[str] = [], filter: Filter = {}
) -> list[models.MenuItem]:
    Session = info.context["Session"]
    query = queries.MenuItem(*ids)

    if name_filter := filter.get("name"):
        query = query.filter_by_name(name_filter)

    with Session() as session:
        result = session.scalars(query.select()).all()

    return result


@query.field("ingredients")
def resolve_ingredients(
    _, info: GraphQLResolveInfo, ids: list[str] = [], filter: Filter = {}
) -> list[models.Ingredient]:
    Session = info.context["Session"]

    query = queries.Ingredient(*ids)

    if name_filter := filter.get("name"):
        query = query.filter_by_name(name_filter)

    with Session() as session:
        result = session.scalars(query.select()).all()

    return result
