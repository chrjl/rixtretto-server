from ariadne import ObjectType

from db import queries

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from db import models
    from graphql import GraphQLResolveInfo

menu_item = ObjectType("MenuItem")


@menu_item.field("variants")
def resolve_variants(menu_item: models.MenuItem, info: GraphQLResolveInfo) -> list[str]:
    Session = info.context["Session"]

    query = queries.MenuItem(menu_item.normalized_name).get("variants")

    with Session() as session:
        result = session.scalars(query).all()

    return result


@menu_item.field("service")
def resolve_service(
    menu_item: models.MenuItem, info: GraphQLResolveInfo
) -> models.Service:
    Session = info.context["Session"]

    with Session() as session:
        session.add(menu_item)
        return menu_item.service


@menu_item.field("recipe")
def resolve_recipe(
    menu_item: models.MenuItem, info: GraphQLResolveInfo
) -> list[models.Ingredient]:
    Session = info.context["Session"]

    with Session() as session:
        session.add(menu_item)
        return menu_item.ingredients
