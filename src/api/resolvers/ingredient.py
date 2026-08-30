from ariadne import ObjectType
from graphql import GraphQLResolveInfo

from db import models, queries

ingredient = ObjectType("Ingredient")


@ingredient.field("parent")
def resolve_parent(
    ingredient: models.Ingredient, info: GraphQLResolveInfo
) -> models.Ingredient | None:
    Session = info.context["Session"]

    with Session() as session:
        session.add(ingredient)
        return ingredient.parent


@ingredient.field("children")
def resolve_children(
    ingredient: models.Ingredient, info: GraphQLResolveInfo
) -> list[models.Ingredient]:
    Session = info.context["Session"]

    with Session() as session:
        session.add(ingredient)
        return ingredient.children


@ingredient.field("ancestors")
def resolve_ancestors(
    ingredient: models.Ingredient, info: GraphQLResolveInfo
) -> list[models.Ingredient]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.Ingredient(ingredient.normalized_name).get("ancestors")
        ).all()


@ingredient.field("descendants")
def resolve_descendants(
    ingredient: models.Ingredient, info: GraphQLResolveInfo
) -> list[models.Ingredient]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.Ingredient(ingredient.normalized_name).get("descendants")
        ).all()


@ingredient.field("menuItems")
def resolve_menu_items(
    ingredient: models.Ingredient, info: GraphQLResolveInfo
) -> list[models.MenuItem]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.Ingredient(ingredient.normalized_name).get("menu_items")
        ).all()
