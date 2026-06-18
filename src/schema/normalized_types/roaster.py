import json
from typing import TypedDict


class RoasterColumns(TypedDict, total=False):
    name: str | None
    city: str | None
    state: str | None
    country: str | None
    equipment_brand: str | None
    equipment_model: str | None
    equipment_capacity: float | None
    details: dict | None


def normalized_roaster_input(input: dict) -> RoasterColumns:
    data = RoasterColumns()

    if name := input.get("name"):
        data["name"] = name

    if location := input.get("location"):
        if "city" in location:
            data["city"] = location["city"]
        if "state" in location:
            data["state"] = location["state"]
        if "country_id" in location:
            data["country"] = location["country_id"]

    if equipment := input.get("equipment"):
        if "brand" in equipment:
            data["equipment_brand"] = equipment["brand"]
        if "model" in equipment:
            data["equipment_model"] = equipment["model"]
        if "capacity" in equipment:
            data["equipment_capacity"] = equipment["capacity"]
    
    if details := input.get("details"):
        data["details"] = json.loads(details)

    return data
