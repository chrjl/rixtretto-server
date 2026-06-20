import csv, json
from . import SAMPLE_DATA_DIR


def roaster_data(path):
    result = []
    details_lookup = {}

    with open(path + "roaster-details.json") as jsonfile:
        jsondata = json.load(jsonfile)

    for row in jsondata:
        details_lookup[row["name"]] = row["details"]

    with open(path + "roasters.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if (name := row["name"]) in details_lookup:
                row["details"] = details_lookup[name]

            row["equipment_capacity"] = (
                float(row["equipment_capacity"]) if row["equipment_capacity"] else None
            )

            result.append(row)

    return result


def sample_roaster_data():
    return roaster_data(SAMPLE_DATA_DIR)


def sample_roaster_objects():
    from db.models import Roaster

    return [Roaster(**row) for row in sample_roaster_data()]


if __name__ == "__main__":
    from sqlalchemy.orm import Session
    from db.main import engine

    with Session(engine) as session:
        session.add_all(sample_roaster_objects())
        session.commit()
