#!/usr/bin/env python3
import os, argparse, json
from datetime import datetime
from sqlalchemy import Engine, select, func, and_
from sqlalchemy.orm import Session
from db.main import engine
from db.models import (
    Country,
    Origin,
    Roaster,
    RoastedCoffee,
    GreenCoffee,
    CoffeeComponent,
)
from db.utilities import is_in_model, normalized_text


def green_coffee_objects(engine: Engine, data):
    result = []

    for item in data:
        origin_data = item.get("origin")
        country_id = origin_data.get("country")
        region_name = origin_data.get("region")
        community = origin_data.get("community")
        details = item.get("details")

        with Session(engine) as session:
            origin = None

            if region_name:
                origin = session.scalar(
                    select(Origin).where(
                        func.lower(Origin._name_n) == normalized_text(region_name)
                    )
                )

            if origin is None:
                if region_name is not None:
                    details["region"] = region_name

                origin = session.scalar(
                    select(Origin).where(
                        Origin.name
                        == select(Country.name).where(Country.id == country_id)
                    )
                )

        result.append(
            GreenCoffee(
                **{
                    **{k: v for k, v in item.items() if is_in_model(GreenCoffee, k)},
                    "origin": origin,
                    "community": community,
                    "details": details or {},
                }
            )
        )

    return result


def roaster_object_and_associations(engine, data):
    roaster_object = Roaster(
        **{k: v for k, v in data.items() if is_in_model(Roaster, k)}
    )

    result = {
        "roaster": roaster_object,
        "coffees": [],
        "component_associations": [],
    }

    for coffee_data in data.get("roasted_coffees", []):
        dates = {}

        if date_added := coffee_data.get("date_added"):
            dates["date_added"] = datetime.fromisoformat(date_added)
        if date_updated := coffee_data.get("date_updated"):
            dates["date_updated"] = datetime.fromisoformat(date_updated)
        if date_removed := coffee_data.get("date_removed"):
            dates["date_removed"] = datetime.fromisoformat(date_removed)

        coffee = RoastedCoffee(
            **{
                **{
                    k: v
                    for k, v in coffee_data.items()
                    if (is_in_model(RoastedCoffee, k) and k not in ["component"])
                },
                **dates,
            }
        )

        roaster_object.coffees.append(coffee)
        result["coffees"].append(coffee)

        for component_data in coffee_data.get("components", []):
            # Find or create the `GreenCoffee` object corresponding to
            # the component, and associate it to the `RoastedCoffee`.

            name = component_data.get("name")
            fraction = (
                100
                if not coffee_data.get("is_blend")
                else component_data.get("fraction")
            )

            dates = {}
            if date_added := coffee_data.get("date_added"):
                dates["date_added"] = datetime.fromisoformat(date_added)
            if date_updated := coffee_data.get("date_updated"):
                dates["date_updated"] = datetime.fromisoformat(date_updated)
            if date_removed := coffee_data.get("date_removed"):
                dates["date_removed"] = datetime.fromisoformat(date_removed)

            # If component name is known, try to find and assign the
            # respective `GreenCoffee` object.
            component = None

            if name:
                with Session(engine) as session:
                    component = session.scalar(
                        select(GreenCoffee).where(GreenCoffee.name == name)
                    )

            if component:
                component_association = CoffeeComponent(
                    roasted_coffee=coffee,
                    green_coffee=component,
                    fraction=fraction,
                    **dates,
                )

            else:
                # Create a component association with the origin.

                country_id = component_data.get("country")
                region_name = component_data.get("region")
                process = component_data.get("process")
                details = {}

                if name:
                    details["name"] = name

                # Try to find `Origin` object for the region.
                origin = None

                with Session(engine) as session:
                    origin = session.scalar(
                        select(Origin).where(Origin.name == region_name)
                    )

                    if not origin:
                        # Use `Origin` object for the country.
                        origin = session.scalar(
                            select(Origin)
                            .join(Origin.country)
                            .where(
                                Origin.name == Country.name,
                                Country.id == country_id,
                            )
                        )

                        if region_name:
                            details["region"] = region_name

                component_association = CoffeeComponent(
                    roasted_coffee=coffee,
                    process=process,
                    origin_id=getattr(origin, "id"),
                    fraction=fraction,
                    **dates,
                )

            coffee.component_associations.append(component_association)
            result["component_associations"].append(component_association)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Seeds the database defined in db/main.py with user-provided sample data."
    )

    parser.add_argument("--json", help="path to json file")
    args = parser.parse_args()

    if (not args.json) or (not os.path.exists(args.json)):
        raise FileNotFoundError()

    with open(args.json) as file:
        data = json.load(file)

    with Session(engine) as session:
        if green_coffee_data := data.get("green_coffees", []):
            with session.begin():
                session.add_all(green_coffee_objects(engine, green_coffee_data))

        with session.begin():
            for roaster_data in data["roasters"]:
                session.add(
                    roaster_object_and_associations(engine, roaster_data).get(
                        "roaster", []
                    )
                )


if __name__ == "__main__":
    main()
