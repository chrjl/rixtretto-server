from __future__ import annotations

from ariadne import ObjectType

from db import models

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