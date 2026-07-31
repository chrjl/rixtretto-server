import csv
from . import SAMPLE_DATA_DIR
from datetime import datetime


def service_roaster_association_data(path):
    service_roaster_associations = {}

    with open(path + "service-roaster-associations.csv") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            service_roaster_associations[row["service_name"]] = row["roaster_name"]

    return service_roaster_associations


def service_location_data(path):
    service_locations = {}

    with open(path + "service-locations.csv") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            if (service_name := row["service_name"]) not in service_locations:
                service_locations[service_name] = []

            service_locations[service_name].append(
                {
                    "association_name": row["association_name"],
                    "description": row["description"],
                    "location_name": row["location_name"],
                    "address": row["address"],
                    "address_detail": row["address_detail"],
                    "neighborhood": row["neighborhood"],
                    "city": row["city"],
                    "state": row["state"],
                    "country_id": row["country_id"],
                    "date_opened": row["date_opened"],
                    "date_closed": row["date_closed"],
                }
            )

    return [
        {
            "service_name": service_name,
            "location_associations": locations,
        }
        for service_name, locations in service_locations.items()
    ]


def sample_service_objects(engine):
    from sqlalchemy.orm import Session
    from db.models import Service, Location, ServiceLocationAssociation
    from db import queries

    sample_service_roaster_associations = service_roaster_association_data(
        SAMPLE_DATA_DIR
    )

    sample_service_location_data = service_location_data(SAMPLE_DATA_DIR)

    result = []

    for row in sample_service_location_data:
        service_name = row.get("service_name")
        service = Service(name=service_name)

        if roaster_name := sample_service_roaster_associations.get(service_name):
            query = (
                queries.Roaster()
                .filter_by_name(filter={"contains": roaster_name})
                .select(["id"])
            )

            with Session(engine) as session:
                roaster_id = session.execute(query).one().id
                service.roaster_id = roaster_id

        for location_data in row["location_associations"]:
            location = Location(
                name=location_data.get("location_name"),
                address=location_data.get("address"),
                city=location_data.get("city"),
                state=location_data.get("state"),
                country_id=location_data.get("country_id"),
            )

            service_location_association = ServiceLocationAssociation(
                name=location_data.get("association_name"),
                location=location,
                description=location_data.get("description"),
            )

            if address_detail := location_data.get("address_detail"):
                service_location_association.address_detail = address_detail

            if neighborhood := location_data.get("neighborhood"):
                service_location_association.neighborhood = neighborhood

            if date_opened := location_data.get("date_opened"):
                service_location_association.date_opened = datetime.fromisoformat(
                    date_opened
                )

            if date_closed := location_data.get("date_closed"):
                service_location_association.date_closed = datetime.fromisoformat(
                    date_closed
                )

            service.location_associations.append(service_location_association)

        result.append(service)

    return result


if __name__ == "__main__":
    from sqlalchemy.orm import Session
    from db.main import engine

    with Session(engine) as session:
        session.add_all(sample_service_objects(engine))
        session.commit()
