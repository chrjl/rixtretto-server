from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict
from ariadne import ObjectType

from db import queries

if TYPE_CHECKING:
    from db import models
    from ariadne.types import GraphQLResolveInfo


class GreenCoffeeSource(TypedDict, total=False):
    name: str | None
    source_type: str | None
    producer_name: str | None
    harvest_year: int | None
    country: models.Country
    origin: models.Origin
    community: str | None


green_coffee = ObjectType("GreenCoffee")


@green_coffee.field("source")
def resolve_green_coffee_source(
    green_coffee: models.GreenCoffee, info: GraphQLResolveInfo
) -> GreenCoffeeSource:
    Session = info.context["Session"]

    with Session() as session:
        origin = session.scalar(queries.GreenCoffee(green_coffee.id).get("origins"))
        country = origin.country

    return {
        "name": green_coffee.source,
        "source_type": green_coffee.source_type,
        "producer_name": green_coffee.details.get("producer_name"),
        "harvest_year": green_coffee.details.get("harvest_year"),
        "country": country,
        "origin": origin,
        "community": green_coffee.community,
    }


@green_coffee.field("processes")
def resolve_green_coffee_processes(
    green_coffee: models.GreenCoffee, info: GraphQLResolveInfo
) -> list[str]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.GreenCoffee(green_coffee.id).get("processes")
        ).all()


@green_coffee.field("varieties")
def resolve_green_coffee_varieties(
    green_coffee: models.GreenCoffee, info: GraphQLResolveInfo
) -> list[str]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.GreenCoffee(green_coffee.id).get("varieties")
        ).all()


@green_coffee.field("tasting")
def resolve_green_coffee_tasting(
    green_coffee: models.GreenCoffee, info: GraphQLResolveInfo
) -> list[str]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.GreenCoffee(green_coffee.id).get("tasting")
        ).all()


@green_coffee.field("roasters")
def resolve_green_coffee_roasters(
    green_coffee: models.GreenCoffee, info: GraphQLResolveInfo
) -> list[models.Roaster]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.GreenCoffee(green_coffee.id).get("roasters")
        ).all()


@green_coffee.field("associations")
def resolve_green_coffee_associations(
    green_coffee: models.GreenCoffee, info: GraphQLResolveInfo
) -> list[models.CoffeeComponent]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.GreenCoffee(green_coffee.id).get("associations")
        ).all()
