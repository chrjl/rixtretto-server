from __future__ import annotations

from ariadne import ObjectType

from .mutation import mutation_type
from db import models
from schema.normalized_types.roaster import normalized_roaster_input

roaster = ObjectType("Roaster")


@roaster.field("location")
def resolve_roaster_location(roaster, info):
    Session = info.context["Session"]

    with Session() as session:
        country = session.get(models.Country, roaster.country)

    return {
        "city": roaster.city,
        "state": roaster.state,
        "country": country,
    }


@roaster.field("equipment")
def resolve_roaster_equipment(roaster, _info):
    return {
        "brand": roaster.equipment_brand,
        "model": roaster.equipment_model,
        "capacity": roaster.equipment_capacity,
    }


@mutation_type.field("roasterCreate")
def resolve_roaster_create(_, info, input):
    if input.get("name") is None:
        return {
            "status": False,
            "error": {"code": 400, "message": "Missing required field `name`"},
        }

    if (
        ("location" not in input)
        or ("country_id" not in input["location"])
        or (input["location"]["country_id"] is None)
    ):
        return {
            "status": False,
            "error": {
                "code": 400,
                "message": "Missing required field `location.countryId`",
            },
        }

    try:
        normalized_input = normalized_roaster_input(input)
    except:
        return {
            "status": False,
            "error": {"code": 400, "message": "Bad Request"},
        }

    Session = info.context["Session"]

    with Session() as session:
        roaster = models.Roaster(**normalized_input)
        session.add(roaster)

        session.commit()
        session.refresh(roaster)

    return {"status": True, "roaster": roaster}


@mutation_type.field("roasterUpdate")
def resolve_roaster_update(_, info, id, input):
    Session = info.context["Session"]

    if "name" in input and input["name"] is None:
        return {
            "status": False,
            "error": {"code": 400, "message": "Cannot unset required field `name`"},
        }

    if "location" in input:
        if input["location"] is None or (
            "country_id" in input["location"]
            and input["location"]["country_id"] is None
        ):
            return {
                "status": False,
                "error": {
                    "code": 400,
                    "message": "Cannot unset required field `location.countryId`",
                },
            }

    with Session() as session:
        roaster = session.get(models.Roaster, id)

        for key, value in normalized_roaster_input(input).items():
            setattr(roaster, key, value)

        session.commit()
        session.refresh(roaster)

    return {"status": True, "roaster": roaster}
