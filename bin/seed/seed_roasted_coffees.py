import csv
from datetime import datetime
from . import SAMPLE_DATA_DIR


def roasted_coffee_data(path):
    list_columns = ["profiles", "tasting"]
    result = []

    with open(path + "roasted-coffee.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            for column in list_columns:
                row[column] = row[column].split(";") if row.get(column) else []

            result.append(row)

    return result


def coffee_association_data(path):
    result = []

    with open(path + "coffee-associations.csv") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            if green_name := row["green_name"]:
                result.append(
                    {"roasted_name": row["roasted_name"], "green_name": green_name}
                )
            elif region_name := row["region_name"]:
                result.append(
                    {"roasted_name": row["roasted_name"], "region_name": region_name}
                )
            elif country_id := row["country_id"]:
                result.append(
                    {"roasted_name": row["roasted_name"], "country_id": country_id}
                )

    return result


def sample_roasted_coffee_data():
    return roasted_coffee_data(SAMPLE_DATA_DIR)


def sample_coffee_association_data():
    return coffee_association_data(SAMPLE_DATA_DIR)


def sample_roasted_coffee_objects(engine):
    from sqlalchemy import select
    from sqlalchemy.orm import Session
    from db import models

    roasted_coffee_data = sample_roasted_coffee_data()
    coffee_association_data = sample_coffee_association_data()

    coffee_association_lookup = {}
    for association in coffee_association_data:
        if (
            roasted_name := association["roasted_name"]
        ) not in coffee_association_lookup:
            coffee_association_lookup[roasted_name] = [association]
        else:
            coffee_association_lookup[roasted_name].append(association)

    roasted_coffee_objects = []
    for roasted_coffee in roasted_coffee_data:
        roasted_coffee_obj = models.RoastedCoffee(name=roasted_coffee["name"])

        if date_added := roasted_coffee.get("date_added"):
            roasted_coffee_obj.date_added = datetime.fromisoformat(date_added)
        if date_removed := roasted_coffee.get("date_removed"):
            roasted_coffee_obj.date_added = datetime.fromisoformat(date_removed)

        # Attach roaster
        with Session(engine) as session:
            roaster_name = roasted_coffee.get("roaster_name")
            roaster_id = session.execute(
                select(models.Roaster.id).where(models.Roaster.name == roaster_name)
            ).scalar()

        if roaster_id is None:
            raise Exception("Roaster not found")

        roasted_coffee_obj.roaster_id = roaster_id

        # Append tags
        for profile in roasted_coffee.get("profiles", []):
            roasted_coffee_obj.tags.append(
                models.RoastedCoffeeTag(type="profile", value=profile)
            )
        for tasting_note in roasted_coffee.get("tasting", []):
            roasted_coffee_obj.tags.append(
                models.RoastedCoffeeTag(type="tasting", value=tasting_note)
            )

        # Append components
        for association in coffee_association_lookup.get(roasted_coffee["name"], []):
            association_obj = models.CoffeeComponent()

            association_obj.fraction = (
                100
                if "single origin" in roasted_coffee.get("profiles", [])
                else roasted_coffee.get("fraction", None)
            )

            if green_name := association.get("green_name"):
                with Session(engine) as session:
                    association_obj.green_id = session.scalar(
                        select(models.GreenCoffee.id).where(
                            models.GreenCoffee.name == green_name
                        )
                    )
            else:
                association_obj.variety = roasted_coffee.get("variety")
                association_obj.process = roasted_coffee.get("process")

                if region_name := association.get("region_name"):
                    with Session(engine) as session:
                        association_obj.origin_id = session.scalar(
                            select(models.Origin.id).where(
                                models.Origin.name == region_name
                            )
                        )
                elif country_id := association.get("country_id"):
                    with Session(engine) as session:
                        association_obj.origin_id = session.scalar(
                            select(models.Origin.id)
                            .join(
                                models.Country,
                                models.Country.name == models.Origin.name,
                            )
                            .where(models.Country.id == country_id)
                        )

            roasted_coffee_obj.component_associations.append(association_obj)

        roasted_coffee_objects.append(roasted_coffee_obj)

    return roasted_coffee_objects


if __name__ == "__main__":
    from sqlalchemy.orm import Session
    from db.main import engine

    print(sample_roasted_coffee_objects(engine))
    with Session(engine) as session:
        session.add_all(sample_roasted_coffee_objects(engine))
        session.commit()
