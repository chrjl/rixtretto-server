import json
from pydantic import StringConstraints, Json, MISSING
from api.types import BaseModel, InputType, ObjectType

from .mutation import mutation_type, LocationInput
from db import models

from typing import Annotated, TYPE_CHECKING

if TYPE_CHECKING:
    from graphql import GraphQLResolveInfo

roaster = ObjectType("Roaster")


@roaster.field("location")
def resolve_roaster_location(roaster: models.Roaster, info: GraphQLResolveInfo):
    Session = info.context["Session"]

    with Session() as session:
        country = session.get(models.Country, roaster.country)

    return {
        "city": roaster.city,
        "state": roaster.state,
        "country": country,
    }


@roaster.field("equipment")
def resolve_roaster_equipment(roaster: models.Roaster, _info):
    return {
        "brand": roaster.equipment_brand,
        "model": roaster.equipment_model,
        "capacity": roaster.equipment_capacity,
    }


class RoastingEquipmentInput(BaseModel):
    brand: str | None | MISSING = MISSING
    model: str | None | MISSING = MISSING
    capacity: float | None | MISSING = MISSING


class RoasterInput(BaseModel):
    name: (
        Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)] | MISSING
    ) = MISSING
    location: LocationInput | MISSING = MISSING
    equipment: RoastingEquipmentInput | MISSING = MISSING
    details: Json[dict] | MISSING = MISSING


class RoasterPatch(BaseModel):
    name: (
        Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)] | MISSING
    ) = MISSING
    city: str | None | MISSING = MISSING
    state: str | None | MISSING = MISSING
    country: (
        Annotated[
            str, StringConstraints(min_length=2, max_length=2, strip_whitespace=True)
        ]
        | MISSING
    ) = MISSING
    equipment_brand: str | None | MISSING = MISSING
    equipment_model: str | None | MISSING = MISSING
    equipment_capacity: float | None | MISSING = MISSING
    details: dict | MISSING = MISSING


def get_roaster_patch(input: RoasterInput) -> RoasterPatch:
    patch = RoasterPatch(name=input.name, details=input.details)

    if input.location is not MISSING:
        patch.city = input.location.city
        patch.state = input.location.state
        patch.country = input.location.country_id

    if input.equipment is not MISSING:
        patch.equipment_brand = input.equipment.brand
        patch.equipment_model = input.equipment.model
        patch.equipment_capacity = input.equipment.capacity

    return patch


roaster_input_type = InputType("RoasterInput", lambda data: RoasterInput(**data))


@mutation_type.field("roasterCreate")
def resolve_roaster_create(_, info: GraphQLResolveInfo, input: RoasterInput):
    Session = info.context["Session"]
    patch = get_roaster_patch(input)

    if patch.name is MISSING:
        raise ValueError("Missing required field `name`")

    if patch.country is MISSING:
        raise ValueError("Missing required field `location.countryId`")

    with Session() as session:
        roaster = models.Roaster(**patch.model_dump())
        session.add(roaster)

        session.commit()
        session.refresh(roaster)

    return {"status": True, "roaster": roaster}


@mutation_type.field("roasterUpdate")
def resolve_roaster_update(_, info: GraphQLResolveInfo, id: int, input: RoasterInput):
    Session = info.context["Session"]
    patch = get_roaster_patch(input)

    with Session() as session:
        roaster = session.get(models.Roaster, id)

        for key, value in patch.model_dump().items():
            setattr(roaster, key, value)

        session.commit()
        session.refresh(roaster)

    return {"status": True, "roaster": roaster}
