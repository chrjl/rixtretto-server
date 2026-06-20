import csv, json
from . import SAMPLE_DATA_DIR


def green_coffee_data(path):
    list_columns = ["processes", "varieties", "tasting"]
    result = []
    details_lookup = {}

    with open(path + "green-coffee-details.json") as jsonfile:
        jsondata = json.load(jsonfile)

    for row in jsondata:
        details_lookup[row["name"]] = row["details"]

    with open(path + "green-coffee.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for column in list_columns:
                row[column] = row[column].split(";") if row.get(column) else []

            if (name := row["name"]) in details_lookup:
                row["details"] = details_lookup[name]

            result.append(row)

    return result


def sample_green_coffee_data():
    return green_coffee_data(SAMPLE_DATA_DIR)


def sample_green_coffee_objects(engine):
    from sqlalchemy import select
    from sqlalchemy.orm import Session
    from db.models import Origin, GreenCoffee, GreenCoffeeTag

    green_coffee_objs = []

    for green_coffee in sample_green_coffee_data():
        if origin_name := green_coffee.get("origin_name"):
            query = select(Origin.id).where(Origin._name == origin_name)

            with Session(engine) as session:
                origin_id = session.scalar(query)
        else:
            origin_id = None

        green_coffee_obj = GreenCoffee(
            name=green_coffee["name"],
            origin_id=origin_id,
            source=green_coffee.get("source"),
            source_type=green_coffee.get("source_type"),
            community=green_coffee.get("community"),
        )

        for process in green_coffee.get("processes", []):
            green_coffee_obj.tags.append(GreenCoffeeTag(type="process", value=process))

        for variety in green_coffee.get("varieties", []):
            green_coffee_obj.tags.append(GreenCoffeeTag(type="variety", value=variety))

        for tasting in green_coffee.get("tasting", []):
            green_coffee_obj.tags.append(GreenCoffeeTag(type="tasting", value=tasting))

        green_coffee_objs.append(green_coffee_obj)

    return green_coffee_objs


if __name__ == "__main__":
    from sqlalchemy.orm import Session
    from db.main import engine

    with Session(engine) as session:
        for green_coffee_obj in sample_green_coffee_objects(engine):
            session.add(green_coffee_obj)
            session.commit()
