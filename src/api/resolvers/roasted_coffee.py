from __future__ import annotations

from typing import TYPE_CHECKING
from ariadne import ObjectType

from db import queries

if TYPE_CHECKING:
    from db import models
    from ariadne.types import GraphQLResolveInfo


roasted_coffee = ObjectType("RoastedCoffee")


@roasted_coffee.field("roaster")
def resolve_roasted_coffee_roasters(
    roasted_coffee: models.RoastedCoffee, info: GraphQLResolveInfo
) -> models.Roaster:
    Session = info.context["Session"]

    with Session() as session:
        session.add(roasted_coffee)
        return roasted_coffee.roaster


@roasted_coffee.field("origins")
def resolve_roasted_coffee_origins(
    roasted_coffee: models.RoastedCoffee, info: GraphQLResolveInfo
) -> list[str]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.RoastedCoffee(roasted_coffee.id).get("origins")
        ).all()


@roasted_coffee.field("profiles")
def resolve_roasted_coffee_profiles(
    roasted_coffee: models.RoastedCoffee, info: GraphQLResolveInfo
) -> list[str]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.RoastedCoffee(roasted_coffee.id).get("profiles")
        ).all()


@roasted_coffee.field("processes")
def resolve_roasted_coffee_processes(
    roasted_coffee: models.RoastedCoffee, info: GraphQLResolveInfo
) -> list[str]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.RoastedCoffee(roasted_coffee.id).get("processes")
        ).all()


@roasted_coffee.field("varieties")
def resolve_roasted_coffee_varieties(
    roasted_coffee: models.RoastedCoffee, info: GraphQLResolveInfo
) -> list[str]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.RoastedCoffee(roasted_coffee.id).get("varieties")
        ).all()


@roasted_coffee.field("tasting")
def resolve_roasted_coffee_tasting(
    roasted_coffee: models.RoastedCoffee, info: GraphQLResolveInfo
) -> list[str]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.RoastedCoffee(roasted_coffee.id).get("tasting")
        ).all()


@roasted_coffee.field("components")
def resolve_roasted_coffee_associations(
    roasted_coffee: models.RoastedCoffee, info: GraphQLResolveInfo
) -> list[models.CoffeeComponent]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.RoastedCoffee(roasted_coffee.id).get("associations")
        ).all()
