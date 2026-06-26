from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict
from ariadne import ObjectType

from db import models, queries
from api.types import (
    GreenCoffeeInput,
    normalized_green_coffee_input,
    normalized_green_coffee_tags,
)
from .mutation import mutation_type

if TYPE_CHECKING:
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


@mutation_type.field("greenCoffeeCreate")
def resolve_green_coffee_create(_, info: GraphQLResolveInfo, input: GreenCoffeeInput):
    Session = info.context["Session"]

    if input.get("name") is None:
        return {
            "status": False,
            "error": {"code": 400, "message": "Missing required field `name`"},
        }

    normalized_input = normalized_green_coffee_input(input)
    normalized_tags = normalized_green_coffee_tags(input)

    with Session() as session:
        green_coffee = models.GreenCoffee(**normalized_input)

        for tag_data in normalized_tags:
            green_coffee.tags.append(models.GreenCoffeeTag(**tag_data))

        session.add(green_coffee)

        session.commit()
        session.refresh(green_coffee)

    return {"status": True, "green_coffee": green_coffee}


@mutation_type.field("greenCoffeeUpdate")
def resolve_green_coffee_update(
    _, info: GraphQLResolveInfo, id: int, input: GreenCoffeeInput
):
    Session = info.context["Session"]

    with Session() as session:
        green_coffee = session.get(models.GreenCoffee, id)

        for key, value in normalized_green_coffee_input(input).items():
            setattr(green_coffee, key, value)

        # clear tag entries
        updated_tags = normalized_green_coffee_tags(input)
        updated_tag_types = set([tag["type"] for tag in updated_tags])

        for tag_obj in green_coffee.tags:
            if tag_obj.type in updated_tag_types:
                session.delete(tag_obj)

        # write new tags
        for tag_data in updated_tags:
            green_coffee.tags.append(models.GreenCoffeeTag(**tag_data))

        session.commit()
        session.refresh(green_coffee)

    return {"status": True, "green_coffee": green_coffee}
