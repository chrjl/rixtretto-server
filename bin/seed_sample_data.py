from sqlalchemy.orm import Session

from bin.seed.seed_roasters import sample_roaster_objects
from bin.seed.seed_green_coffees import sample_green_coffee_objects
from bin.seed.seed_roasted_coffees import sample_roasted_coffee_objects
from db.main import engine

with Session(engine) as session:
    session.add_all(sample_roaster_objects())
    session.add_all(sample_green_coffee_objects(engine))
    session.commit()

    session.add_all(sample_roasted_coffee_objects(engine))
    session.commit()
