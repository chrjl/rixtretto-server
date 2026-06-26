import csv, json
from sqlalchemy import select
from sqlalchemy.orm import Session

from db import models
from db.main import engine

from . import SAMPLE_DATA_DIR


def green_coffee_data(path):
    simple_columns = ["name", "source", "source_type", "origin_name", "community"]
    list_columns = ["processes", "varieties", "tasting"]
    csvdata = []

    with open(path + "green-coffee.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row_data = {}

            for column in simple_columns:
                row_data[column] = row[column]
            for column in list_columns:
                row_data[column] = row[column].split(";") if row.get(column) else []

            csvdata.append(row_data)

    with open(path + "green-coffee-details.json") as jsonfile:
        jsondata = json.load(jsonfile)

    lookup = {row["name"]: row for row in csvdata}

    for row in jsondata:
        name = row["name"]

        if name in lookup:
            lookup[name]["details"] = row["details"]
        else:
            lookup[name] = {"details": row["details"]}

    return [*lookup.values()]


def sample_green_coffee_data():
    return green_coffee_data(SAMPLE_DATA_DIR)


def sample_green_coffee_objects(engine):
    green_coffee_objs = []

    for green_coffee in sample_green_coffee_data():
        if origin_name := green_coffee.get("origin_name"):
            query = select(models.Origin.id).where(models.Origin._name == origin_name)

            with Session(engine) as session:
                origin_id = session.scalar(query)
        else:
            origin_id = None

        green_coffee_obj = models.GreenCoffee(
            name=green_coffee["name"],
            origin_id=origin_id,
            source=green_coffee.get("source"),
            source_type=green_coffee.get("source_type"),
            community=green_coffee.get("community"),
        )

        for process in green_coffee.get("processes", []):
            green_coffee_obj.tags.append(
                models.GreenCoffeeTag(type="process", value=process)
            )

        for variety in green_coffee.get("varieties", []):
            green_coffee_obj.tags.append(
                models.GreenCoffeeTag(type="variety", value=variety)
            )

        for tasting in green_coffee.get("tasting", []):
            green_coffee_obj.tags.append(
                models.GreenCoffeeTag(type="tasting", value=tasting)
            )

        green_coffee_objs.append(green_coffee_obj)

    return green_coffee_objs


if __name__ == "__main__":
    result = sample_green_coffee_objects(engine)

    for green_coffee_obj in result:
        print(green_coffee_obj, *green_coffee_obj.tags)
