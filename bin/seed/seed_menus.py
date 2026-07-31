import csv
from datetime import datetime

from . import SAMPLE_DATA_DIR
from db.utilities import normalized_text


def ingredient_data(path):
    with open(path + "ingredients.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        return [*reader]


def menu_item_data(path):
    result = []

    with open(path + "menu-items.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            result.append(
                {
                    "name": row["name"],
                    "service_name": row["service_name"],
                    "date_added": (
                        datetime.fromisoformat(row["date_added"])
                        if row["date_added"]
                        else None
                    ),
                    "date_removed": (
                        datetime.fromisoformat(row["date_removed"])
                        if row["date_added"]
                        else None
                    ),
                    "variants": row["variants"].split(";"),
                    "ingredients": row["ingredients"].split(";"),
                }
            )

    return result


def sample_ingredient_objects(engine):
    from sqlalchemy.orm import Session
    from db.models import Ingredient

    result = []

    for row in ingredient_data(SAMPLE_DATA_DIR):
        ingredient_name = row["name"]
        children = row["children"].split(";") if row["children"] else []

        with Session(engine) as session:
            if not (
                session.get(Ingredient, normalized_text(ingredient_name))
                or ingredient_name in [ingredient.name for ingredient in result]
            ):

                result.append(Ingredient(name=ingredient_name))

            for child_name in children:
                child = session.get(Ingredient, normalized_text(child_name))

                if not child:
                    child = Ingredient(name=child_name)

                child.parent_name = normalized_text(ingredient_name)
                result.append(child)

    return result


def sample_menu_item_objects(engine):
    from sqlalchemy.orm import Session

    from db.models import MenuItem, MenuItemVariant, MenuItemIngredientAssociation
    from db import queries

    result = []

    for row in menu_item_data(SAMPLE_DATA_DIR):
        menu_item = MenuItem(name=row["name"])
        service_name = row.get("service_name")

        with Session(engine) as session:

            service_id: int | None = getattr(
                session.execute(
                    queries.Service()
                    .filter_by_name({"starts_with": service_name})
                    .select(["id"])
                ).first(),
                "id",
            )

            if not service_id:
                raise AttributeError

            menu_item.service_id = service_id

        if date_added := row.get("date_added"):
            menu_item.date_added = date_added
        if date_removed := row.get("date_added"):
            menu_item.date_removed = date_removed

        for variant in row.get("variants", []):
            menu_item.variants.append(MenuItemVariant(variant=variant))

        if ingredient_names := row.get("ingredients"):
            for ingredient_name in ingredient_names:
                ingredient_association = MenuItemIngredientAssociation(
                    service_id=service_id,
                    menu_item_pkey=menu_item.name,
                    ingredient_pkey=normalized_text(ingredient_name),
                )

                menu_item.ingredient_associations.append(ingredient_association)

        result.append(menu_item)

    return result


def seed_objects():
    from db.main import engine
    from sqlalchemy.orm import Session

    ingredient_objects = sample_ingredient_objects(engine)

    with Session(engine) as session:
        session.add_all(ingredient_objects)
        session.commit()

        session.add_all(sample_menu_item_objects(engine))
        session.commit()


if __name__ == "__main__":
    seed_objects()
