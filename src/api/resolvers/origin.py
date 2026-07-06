from __future__ import annotations

from ariadne import ObjectType
from ariadne.types import GraphQLResolveInfo

# from sqlalchemy.orm import Session

from db.main import engine
from db import queries

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Sequence
    from db import models

origin = ObjectType("Origin")


@origin.field("parent")
def resolve_origin_parent(
    origin: models.Origin, info: GraphQLResolveInfo
) -> models.Origin:
    Session = info.context["Session"]

    with Session() as session:
        session.add(origin)
        result = origin.parent

    return result


@origin.field("children")
def resolve_origin_children(
    origin: models.Origin, info: GraphQLResolveInfo
) -> Sequence[models.Origin]:
    Session = info.context["Session"]

    with Session() as session:
        session.add(origin)
        result = origin.children

    return result


@origin.field("suborigins")
def resolve_origin_suborigins(
    origin: models.Origin, info: GraphQLResolveInfo
) -> Sequence[models.Origin]:
    Session = info.context["Session"]

    with Session() as session:
        result = session.scalars(
            queries.Origin().filter_by_ids(ids=[origin.id]).get("suborigins")
        ).all()

    return result


@origin.field("country")
def resolve_origin_country(
    origin: models.Origin, info: GraphQLResolveInfo
) -> models.Country:
    Session = info.context["Session"]

    with Session() as session:
        session.add(origin)
        result = origin.country

    return result


@origin.field("roastedCoffees")
def resolve_roasted_coffees_of_origin(
    origin: models.Origin, info: GraphQLResolveInfo
) -> Sequence[models.RoastedCoffee]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.Origin().filter_by_ids(ids=[origin.id]).get("roasted_coffees")
        ).all()


@origin.field("greenCoffees")
def resolve_green_coffees_of_origin(
    origin: models.Origin, info: GraphQLResolveInfo
) -> Sequence[models.GreenCoffee]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.Origin().filter_by_ids(ids=[origin.id]).get("green_coffees")
        ).all()


@origin.field("roasters")
def resolve_roasters_of_origin(
    origin: models.Origin, info: GraphQLResolveInfo
) -> Sequence[models.Roaster]:
    Session = info.context["Session"]

    with Session() as session:
        session.add(origin)

        return session.scalars(
            queries.Origin().filter_by_ids(ids=[origin.id]).get("roasters")
        ).all()
