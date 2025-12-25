#!/usr/bin/env python3
import os, argparse, json
from sqlalchemy import select
from sqlalchemy.orm import Session
from db.main import engine
from db.models import Origin, Roaster, RoastedCoffee, GreenCoffee


def main():
    parser = argparse.ArgumentParser(
        description="Seeds the database defined in db/main.py with user-provided sample data."
    )

    parser.add_argument("--json", help="path to json file")
    args = parser.parse_args()

    if (not args.json) or (not os.path.exists(args.json)):
        raise FileNotFoundError()

    with open(args.json) as file:
        text = file.read()
        data = json.loads(text)

    with Session(engine) as session:
        for entry in data["roasters"]:
            session.add(
                Roaster(
                    name=entry.get("name"),
                    city=entry.get("city"),
                    state=entry.get("state"),
                    country=entry.get("country"),
                    details=entry.get("details"),
                    equipment_brand=entry.get("equipment_brand"),
                    equipment_model=entry.get("equipment_model"),
                    equipment_capacity=entry.get("equipment_capacity"),
                )
            )

        for entry in data["roasted_coffees"]:
            roaster_id = session.scalar(
                select(Roaster.id).where(Roaster.name == entry["roaster"])
            )
            session.add(
                RoastedCoffee(
                    roaster_id=roaster_id,
                    name=entry.get("name"),
                    is_blend=entry.get("is_blend"),
                    profile=entry.get("profile"),
                    notes=entry.get("notes"),
                    prices=entry.get("prices"),
                )
            )

        for country, regions in data["origins"].items():
            session.add(Origin(country=country))

            for region in regions:
                session.add(Origin(country=country, region=region))

        for coffee in data["green_coffees"]:
            region_id = session.scalar(
                select(Origin.id).where(Origin.region == coffee["region"])
            )

            session.add(
                GreenCoffee(
                    name=coffee.get("name"),
                    process=coffee.get("process"),
                    source=coffee.get("source"),
                    source_type=coffee.get("source_type"),
                    region_id=region_id,
                    varieties=coffee.get("varieties"),
                    details=coffee.get("details"),
                )
            )

        session.flush()

        if input("Commit changes? [y|n]: ") == "y":
            session.commit()


if __name__ == "__main__":
    main()
