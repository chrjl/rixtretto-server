import json
from typing import TypedDict, Required

from db import models


class Error(TypedDict):
    code: int
    message: str


class LocationInput(TypedDict, total=False):
    city: str | None
    state: str | None
    country_id: str | None


class RoastingEquipmentInput(TypedDict, total=False):
    brand: str | None
    model: str | None
    capacity: float | None


class RoasterInput(TypedDict, total=False):
    name: str | None
    location: LocationInput | None
    equipment: RoastingEquipmentInput | None
    details: str | None


class RoasterColumns(TypedDict, total=False):
    name: str | None
    city: str | None
    state: str | None
    country: str | None
    equipment_brand: str | None
    equipment_model: str | None
    equipment_capacity: float | None
    details: dict | None


def normalized_roaster_input(input: RoasterInput) -> RoasterColumns:
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


class GreenCoffeeSourceInput(TypedDict, total=False):
    name: str | None
    type: str | None
    origin_id: int | None
    community: str | None
    details: str


class GreenCoffeeInput(TypedDict, total=False):
    name: str | None
    source: GreenCoffeeSourceInput
    details: str

    processes: list[str] | None
    varieties: list[str] | None
    tasting: list[str] | None


class GreenCoffeeColumns(TypedDict, total=False):
    name: str | None
    origin_id: int | None
    source: str | None
    source_type: str | None
    community: str | None
    details: dict
    processes: list[str] | None
    varieties: list[str] | None
    tasting: list[str] | None


class GreenCoffeeTagsColumns(TypedDict, total=False):
    green_id: int | None
    type: Required[str]
    value: Required[str]


def normalized_green_coffee_input(input: GreenCoffeeInput) -> GreenCoffeeColumns:
    data = GreenCoffeeColumns()

    if "details" in input:
        data["details"] = json.loads(input["details"])

    if "name" in input:
        data["name"] = input["name"]

    if "source" in input:
        source = input["source"]

        if "name" in source:
            data["source"] = source["name"]
        if "type" in source:
            data["source_type"] = source["type"]
        if "origin_id" in source:
            data["origin_id"] = source["origin_id"]
        if "community" in source:
            data["community"] = source["community"]
        if "details" in source:
            if "details" in data:
                data["details"].update(json.loads(source["details"]))
            else:
                data["details"] = json.loads(source["details"])

    return data


def normalized_green_coffee_tags(
    input: GreenCoffeeInput,
) -> list[GreenCoffeeTagsColumns]:
    data = []

    if processes := input.get("processes", []):
        for process in processes:
            data.append(GreenCoffeeTagsColumns(type="process", value=process))
    if varieties := input.get("varieties", []):
        for variety in varieties:
            data.append(GreenCoffeeTagsColumns(type="variety", value=variety))
    if tasting := input.get("tasting", []):
        for tasting_note in tasting:
            data.append(GreenCoffeeTagsColumns(type="tasting", value=tasting_note))

    return data


class RoastedCoffeeInput(TypedDict, total=False):
    name: str | None
    roaster_id: int | None
    date_added: str | None
    date_removed: str | None
    profiles: list[str]
    tasting: list[str]


class RoastedCoffeeMutationResult(TypedDict, total=False):
    status: Required[bool]
    error: Error | None
    roasted_coffee: models.RoastedCoffee | None


class CoffeeTagInput(TypedDict, total=False):
    type: Required[str]
    values: list[str]


class CoffeeComponentInput(TypedDict, total=False):
    green_id: int
    origin_id: int
    process: str
    variety: str
    fraction: int


class CoffeeComponentMutationResult(TypedDict, total=False):
    status: Required[bool]
    error: Error
    roasted_coffee: models.RoastedCoffee
    green_coffee: models.GreenCoffee | None
    origin: models.Origin | None
