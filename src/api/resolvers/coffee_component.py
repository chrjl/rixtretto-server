from __future__ import annotations

from ariadne import ObjectType

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ariadne.types import GraphQLResolveInfo
    from db import models

component_association = ObjectType("CoffeeComponent")


@component_association.field("roastedCoffee")
def resolve_roasted_coffee(
    association: models.CoffeeComponent, info: GraphQLResolveInfo
) -> models.RoastedCoffee:
    context = info.context
    Session = context["Session"]

    with Session() as session:
        session.add(association)
        result = association.roasted_coffee

    return result


@component_association.field("greenCoffee")
def resolve_green_coffee(
    association: models.CoffeeComponent, info: GraphQLResolveInfo
) -> models.GreenCoffee:
    context = info.context
    Session = context["Session"]

    with Session() as session:
        session.add(association)
        result = association.green_coffee

    return result


@component_association.field("origin")
def resolve_origin(
    association: models.CoffeeComponent, info: GraphQLResolveInfo
) -> models.Origin:
    context = info.context
    Session = context["Session"]

    with Session() as session:
        session.add(association)
        result = association.origin

    return result
