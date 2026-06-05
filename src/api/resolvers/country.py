from __future__ import annotations
from ariadne import ObjectType

from db import queries

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db import models
    from ariadne.types import GraphQLResolveInfo


country = ObjectType("Country")


@country.field("origin")
def resolve_origin_of_country(
    country: models.Country, info: GraphQLResolveInfo
) -> models.Origin:
    Session = info.context["Session"]

    with Session() as session:
        result = session.scalar(
            queries.Country().filter_by_ids([country.id]).get("origin")
        )

    return result


@country.field("roasters")
def resolve_roasters_of_country(
    country: models.Country, info: GraphQLResolveInfo
) -> list[models.Roaster]:
    Session = info.context["Session"]

    return []


@country.field("roastedCoffees")
def resolve_roasted_coffees_of_country(
    country: models.Country, info: GraphQLResolveInfo
) -> list[models.RoastedCoffee]:
    Session = info.context["Session"]

    return []


@country.field("greenCoffees")
def resolve_green_coffees_of_country(
    country: models.Country, info: GraphQLResolveInfo
) -> list[models.GreenCoffee]:
    Session = info.context["Session"]

    return []
