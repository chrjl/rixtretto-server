import csv, json
from . import SAMPLE_DATA_DIR

from db.models import Roaster


def roaster_data(path):
    with open(path + "roasters.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        csvdata = [*reader]

    with open(path + "roaster-details.json") as jsonfile:
        jsondata = json.load(jsonfile)

    lookup = {row["name"]: row for row in csvdata}

    for row in jsondata:
        name = row["name"]

        if name in lookup:
            lookup[name]["details"] = row["details"]
        else:
            lookup[name] = {"details": row["details"]}

    return [*lookup.values()]


def sample_roaster_data():
    return roaster_data(SAMPLE_DATA_DIR)


def sample_roaster_objects():
    return [Roaster(**row) for row in sample_roaster_data()]


if __name__ == "__main__":
    print(sample_roaster_objects())
