from sqlalchemy.orm import Session

from bin.seed.seed_roasters import sample_roaster_objects
from bin.seed.seed_coffee_tags import sample_coffee_tag_type_objects
from bin.seed.seed_green_coffees import sample_green_coffee_objects
from bin.seed.seed_roasted_coffees import sample_roasted_coffee_objects
from bin.seed.seed_service import (
    sample_service_objects,
    sample_service_coffee_association_objects,
)
from bin.seed.seed_menus import sample_ingredient_objects, sample_menu_item_objects
from db import models


def seed_sample_data(engine):
    with Session(engine) as session:
        for tag_type in sample_coffee_tag_type_objects():
            if session.get(models.CoffeeTagType, tag_type.name) is None:
                session.add(tag_type)
        session.commit()

        session.add_all(sample_roaster_objects())
        session.add_all(sample_green_coffee_objects(engine))
        session.commit()

        session.add_all(sample_roasted_coffee_objects(engine))
        session.commit()

        session.add_all(sample_service_objects(engine))
        session.commit()

        session.add_all(sample_service_coffee_association_objects(engine))
        session.commit()

        session.add_all(sample_ingredient_objects(engine))
        session.commit()

        session.add_all(sample_menu_item_objects(engine))
        session.commit()


if __name__ == "__main__":
    from db.main import engine

    seed_sample_data(engine)
