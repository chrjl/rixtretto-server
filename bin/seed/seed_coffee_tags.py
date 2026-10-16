import csv, json
from . import SAMPLE_DATA_DIR


def coffee_tag_type_data(path):
    result = []

    with open(path + "coffee-tags.csv") as csvfile:
        reader = csv.DictReader(csvfile, quoting=csv.QUOTE_NOTNULL)
        for row in reader:
            result.append(row)

    return result


def sample_coffee_tag_type_data():
    return coffee_tag_type_data(SAMPLE_DATA_DIR)


def sample_coffee_tag_type_objects():
    from db.models import CoffeeTagType

    return [
        CoffeeTagType(name=row["name"], description=row["description"])
        for row in sample_coffee_tag_type_data()
    ]


if __name__ == "__main__":
    from sqlalchemy.orm import Session
    from db.main import engine
    from db.models import CoffeeTagType

    with Session(engine) as session:
        for coffee_tag_type in sample_coffee_tag_type_objects():
            if session.get(CoffeeTagType, coffee_tag_type.name) is None:
                session.add(coffee_tag_type)
