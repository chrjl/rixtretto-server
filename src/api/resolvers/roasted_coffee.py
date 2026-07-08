from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime
from ariadne import ObjectType

from db import models, queries
from .mutation import mutation_type
from api.types import (
    RoastedCoffeeInput,
    RoastedCoffeeMutationResult,
    CoffeeComponentInput,
    CoffeeComponentMutationResult,
)

if TYPE_CHECKING:
    from ariadne.types import GraphQLResolveInfo

SUPPORTED_TAG_TYPES = ["profile", "tasting"]

roasted_coffee = ObjectType("RoastedCoffee")


@roasted_coffee.field("roaster")
def resolve_roasted_coffee_roasters(
    roasted_coffee: models.RoastedCoffee, info: GraphQLResolveInfo
) -> models.Roaster:
    Session = info.context["Session"]

    with Session() as session:
        session.add(roasted_coffee)
        return roasted_coffee.roaster


@roasted_coffee.field("origins")
def resolve_roasted_coffee_origins(
    roasted_coffee: models.RoastedCoffee, info: GraphQLResolveInfo
) -> list[str]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.RoastedCoffee(roasted_coffee.id).get("origins")
        ).all()


@roasted_coffee.field("profiles")
def resolve_roasted_coffee_profiles(
    roasted_coffee: models.RoastedCoffee, info: GraphQLResolveInfo
) -> list[str]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.RoastedCoffee(roasted_coffee.id).get("profiles")
        ).all()


@roasted_coffee.field("processes")
def resolve_roasted_coffee_processes(
    roasted_coffee: models.RoastedCoffee, info: GraphQLResolveInfo
) -> list[str]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.RoastedCoffee(roasted_coffee.id).get("processes")
        ).all()


@roasted_coffee.field("varieties")
def resolve_roasted_coffee_varieties(
    roasted_coffee: models.RoastedCoffee, info: GraphQLResolveInfo
) -> list[str]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.RoastedCoffee(roasted_coffee.id).get("varieties")
        ).all()


@roasted_coffee.field("tasting")
def resolve_roasted_coffee_tasting(
    roasted_coffee: models.RoastedCoffee, info: GraphQLResolveInfo
) -> list[str]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.RoastedCoffee(roasted_coffee.id).get("tasting")
        ).all()


@roasted_coffee.field("components")
def resolve_roasted_coffee_associations(
    roasted_coffee: models.RoastedCoffee, info: GraphQLResolveInfo
) -> list[models.CoffeeComponent]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.RoastedCoffee(roasted_coffee.id).get("associations")
        ).all()


@roasted_coffee.field("dateAdded")
def resolve_roasted_coffee_date_added(roasted_coffee: models.RoastedCoffee, _info):
    if date_added := roasted_coffee.date_added:
        return datetime.isoformat(date_added)

    return None


@roasted_coffee.field("dateRemoved")
def resolve_roasted_coffee_date_removed(roasted_coffee: models.RoastedCoffee, _info):
    if date_removed := roasted_coffee.date_removed:
        return datetime.isoformat(date_removed)

    return None


@mutation_type.field("roastedCoffeeCreate")
def resolve_roasted_coffee_create(
    _,
    info: GraphQLResolveInfo,
    input: RoastedCoffeeInput,
) -> RoastedCoffeeMutationResult:
    Session = info.context["Session"]

    if not input.get("name"):
        return {
            "status": False,
            "error": {"code": 400, "message": "Missing required field `name`"},
        }

    if not input.get("roaster_id"):
        return {
            "status": False,
            "error": {"code": 400, "message": "Missing required field `roasterId`"},
        }

    roasted_coffee_obj = models.RoastedCoffee(
        name=input.get("name"),
        roaster_id=input.get("roaster_id"),
    )

    try:
        if date_added := input.get("date_added"):
            roasted_coffee_obj.date_added = datetime.fromisoformat(date_added)

        if date_removed := input.get("date_removed"):
            roasted_coffee_obj.date_removed = datetime.fromisoformat(date_removed)
    except ValueError:
        return {
            "status": False,
            "error": {
                "code": 400,
                "message": "Datetime fields not in iso formatDatetime fields not in iso format",
            },
        }

    for value in input.get("profiles", []):
        roasted_coffee_obj.tags.append(
            models.RoastedCoffeeTag(type="profile", value=value)
        )

    for value in input.get("tasting", []):
        roasted_coffee_obj.tags.append(
            models.RoastedCoffeeTag(type="tasting", value=value)
        )

    with Session() as session:
        session.add(roasted_coffee_obj)
        session.commit()

        session.refresh(roasted_coffee_obj)

    return {"status": True, "roasted_coffee": roasted_coffee_obj}


@mutation_type.field("roastedCoffeeUpdate")
def resolve_roasted_coffee_update(
    _,
    info: GraphQLResolveInfo,
    id: int,
    input: RoastedCoffeeInput,
) -> RoastedCoffeeMutationResult:
    Session = info.context["Session"]

    with Session() as session:
        roasted_coffee = session.get(models.RoastedCoffee, id)

        if "name" in input:
            if input["name"] is None:
                return {
                    "status": False,
                    "error": {
                        "code": 400,
                        "message": "Cannot unset required field `name`",
                    },
                }
            roasted_coffee.name = input["name"]

        if "roaster_id" in input:
            if input["roaster_id"] is None:
                return {
                    "status": False,
                    "error": {
                        "code": 400,
                        "message": "Cannot unset required field `roaster_id`",
                    },
                }
            roasted_coffee.roaster_id = input["roaster_id"]

        for column in ["dateAdded", "dateRemoved"]:
            if column in input:
                if column is None:
                    setattr(roasted_coffee, column, None)
                else:
                    try:
                        setattr(
                            roasted_coffee,
                            column,
                            datetime.fromisoformat(input[column]),
                        )
                    except ValueError:
                        return {
                            "status": False,
                            "error": {
                                "code": 400,
                                "message": "Datetime fieldsCannot unset required field `roaster_id`",
                            },
                        }

        if "profiles" in input:
            # Reset tags
            session.execute(
                queries.RoastedCoffee().clear_tag(roasted_id=id, type="profile")
            )
            # Write new tags
            roasted_coffee.tags.extend(
                [
                    models.RoastedCoffeeTag(type="profile", value=value)
                    for value in input["profiles"]
                ]
            )

        if "tasting" in input:
            # Reset tags
            session.execute(
                queries.RoastedCoffee().clear_tag(roasted_id=id, type="tasting")
            )
            # Write new tags
            roasted_coffee.tags.extend(
                [
                    models.RoastedCoffeeTag(type="tasting", value=value)
                    for value in input["tasting"]
                ]
            )

        session.commit()
        session.refresh(roasted_coffee)

    return {"status": True, "roasted_coffee": roasted_coffee}


@mutation_type.field("roastedCoffeeTagAdd")
def resolve_roasted_coffee_tag_add(
    _, info: GraphQLResolveInfo, id: int, type: str, values: list[str]
) -> RoastedCoffeeMutationResult:
    Session = info.context["Session"]

    if type not in SUPPORTED_TAG_TYPES:
        return {
            "status": False,
            "error": {"code": 400, "message": f"Unsupported tag type `{type}`"},
        }

    with Session() as session:
        for value in values:
            session.add(models.RoastedCoffeeTag(roasted_id=id, type=type, value=value))

        session.commit()
        roasted_coffee = session.get(models.RoastedCoffee, id)

    return {"status": True, "roasted_coffee": roasted_coffee}


@mutation_type.field("roastedCoffeeTagDelete")
def resolve_roasted_coffee_tag_delete(
    _, info: GraphQLResolveInfo, id: int, type: str, values: list[str] | None = None
) -> RoastedCoffeeMutationResult:
    Session = info.context["Session"]

    if type not in SUPPORTED_TAG_TYPES:
        return {
            "status": False,
            "error": {"code": 400, "message": f"Unsupported tag type `{type}`"},
        }

    with Session() as session:
        if values is None:
            session.execute(queries.RoastedCoffee().clear_tag(roasted_id=id, type=type))

        else:
            session.execute(
                queries.RoastedCoffee().delete_tags(
                    roasted_id=id, type=type, values=values
                )
            )

        session.commit()
        roasted_coffee = session.get(models.RoastedCoffee, id)

    return {"status": True, "roasted_coffee": roasted_coffee}


@mutation_type.field("roastedCoffeeComponentAdd")
def resolve_roasted_coffee_component_add(
    _,
    info: GraphQLResolveInfo,
    id: int,
    input: CoffeeComponentInput,
) -> CoffeeComponentMutationResult:
    Session = info.context["Session"]

    roasted_id = id
    green_id = input.get("green_id")
    origin_id = input.get("origin_id")
    process = input.get("process")
    variety = input.get("variety")
    fraction = input.get("fraction")

    if (green_id is None) and (origin_id is None):
        return {
            "status": False,
            "error": {
                "code": 400,
                "message": "Missing required parameter: either `greenId` or `originId` must be specified.",
            },
        }

    if (green_id is not None) and (origin_id is not None):
        return {
            "status": False,
            "error": {
                "code": 400,
                "message": "Too many parameters: only one of either `greenId` or `originId` must be specified.",
            },
        }

    with Session() as session:
        roasted_coffee = session.get(models.RoastedCoffee, roasted_id)

        component_association = models.CoffeeComponent(
            roasted_id=roasted_id,
            fraction=fraction,
        )

        if green_id is not None:
            component_association.green_id = green_id
        elif origin_id is not None:
            component_association.origin_id = origin_id
            component_association.process = process
            component_association.variety = variety

        roasted_coffee.component_associations.append(component_association)
        session.commit()

        session.refresh(roasted_coffee)

        green_coffee = (
            session.get(models.GreenCoffee, green_id) if green_id is not None else None
        )
        origin = (
            session.get(models.Origin, origin_id) if origin_id is not None else None
        )

    return {
        "status": True,
        "roasted_coffee": roasted_coffee,
        "green_coffee": green_coffee,
        "origin": origin,
    }


@mutation_type.field("roastedCoffeeComponentDelete")
def resolve_roasted_coffee_component_delete(
    _, info: GraphQLResolveInfo, id: int, input: CoffeeComponentInput
) -> CoffeeComponentMutationResult:
    Session = info.context["Session"]

    roasted_id = id
    green_id = input.get("green_id")
    origin_id = input.get("origin_id")
    process = input.get("process")
    variety = input.get("variety")

    if (green_id is None) and (origin_id is None):
        return {
            "status": False,
            "error": {
                "code": 400,
                "message": "Missing required parameter: either `greenId` or `originId` must be specified.",
            },
        }

    if (green_id is not None) and (origin_id is not None):
        return {
            "status": False,
            "error": {
                "code": 400,
                "message": "Too many parameters: only one of either `greenId` or `originId` must be specified.",
            },
        }

    with Session() as session:
        session.execute(
            queries.RoastedCoffee().delete_component(
                roasted_id=roasted_id,
                green_id=green_id,
                origin_id=origin_id,
                process=process,
                variety=variety,
            )
        )

        session.commit()
        roasted_coffee = session.get(models.RoastedCoffee, roasted_id)

    return {"status": True, "roasted_coffee": roasted_coffee}


@mutation_type.field("roastedCoffeeComponentUpdate")
def resolve_roasted_coffee_component_update(
    _, info: GraphQLResolveInfo, id: int, input: CoffeeComponentInput
) -> CoffeeComponentMutationResult:
    Session = info.context["Session"]

    roasted_id = id
    green_id = input.get("green_id")
    origin_id = input.get("origin_id")
    process = input.get("process")
    variety = input.get("variety")
    fraction = input.get("fraction")

    if (green_id is None) and (origin_id is None):
        return {
            "status": False,
            "error": {
                "code": 400,
                "message": "Missing required parameter: either `greenId` or `originId` must be specified.",
            },
        }

    if (green_id is not None) and (origin_id is not None):
        return {
            "status": False,
            "error": {
                "code": 400,
                "message": "Too many parameters: only one of either `greenId` or `originId` must be specified.",
            },
        }

    with Session() as session:
        roasted_coffee = session.get(models.RoastedCoffee, roasted_id)

        if roasted_coffee is None:
            return {
                "status": False,
                "error": {
                    "code": 404,
                    "message": f"Roasted coffee with id `{roasted_id}` not found",
                },
            }

        session.execute(
            queries.RoastedCoffee().update_component(
                roasted_id=roasted_id,
                green_id=green_id,
                origin_id=origin_id,
                process=process,
                variety=variety,
                fraction=fraction,
            )
        )

        session.commit()
        session.refresh(roasted_coffee)

    return {"status": True, "roasted_coffee": roasted_coffee}
