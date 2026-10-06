from ariadne import ObjectType, InputType
from pydantic import StringConstraints, MISSING, model_validator
from typing import Annotated, Self, TYPE_CHECKING
from datetime import datetime
from api.types import BaseModel

from .mutation import mutation_type, CoffeeTagInput
from db import models, queries

if TYPE_CHECKING:
    from graphql import GraphQLResolveInfo

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


@roasted_coffee.field("service")
def resolve_service(
    roasted_coffee: models.RoastedCoffee, info: GraphQLResolveInfo
) -> list[models.Service]:
    Session = info.context["Session"]

    with Session() as session:
        session.add(roasted_coffee)
        return roasted_coffee.service


class RoastedCoffeeInput(BaseModel):
    name: (
        Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)] | MISSING
    ) = MISSING
    roaster_id: int | MISSING = MISSING
    date_added: datetime | None | MISSING = MISSING
    date_removed: datetime | None | MISSING = MISSING
    profiles: list[str] | MISSING = MISSING
    tasting: list[str] | MISSING = MISSING


roasted_coffee_input_type = InputType(
    "RoastedCoffeeInput", lambda data: RoastedCoffeeInput(**data)
)


@mutation_type.field("roastedCoffeeCreate")
def resolve_roasted_coffee_create(
    _,
    info: GraphQLResolveInfo,
    input: RoastedCoffeeInput,
):
    Session = info.context["Session"]

    if input.name is MISSING or not input.name:
        return {
            "status": False,
            "error": {"code": 400, "message": "Missing required field `name`"},
        }

    if input.roaster_id is MISSING:
        return {
            "status": False,
            "error": {"code": 400, "message": "Missing required field `roasterId`"},
        }

    roasted_coffee = models.RoastedCoffee(
        name=input.name,
        roaster_id=input.roaster_id,
        date_added=input.date_added,
        date_removed=input.date_removed,
    )

    if input.profiles is not MISSING:
        roasted_coffee.tags.extend(
            [
                models.RoastedCoffeeTag(type="profile", value=profile)
                for profile in input.profiles
            ]
        )

    if input.tasting is not MISSING:
        roasted_coffee.tags.extend(
            [
                models.RoastedCoffeeTag(type="tasting", value=note)
                for note in input.tasting
            ]
        )

    with Session() as session:
        session.add(roasted_coffee)
        session.commit()

        session.refresh(roasted_coffee)

    return {"status": True, "roasted_coffee": roasted_coffee}


@mutation_type.field("roastedCoffeeUpdate")
def resolve_roasted_coffee_update(
    _,
    info: GraphQLResolveInfo,
    id: int,
    input: RoastedCoffeeInput,
):
    Session = info.context["Session"]

    with Session() as session:
        roasted_coffee = session.get(models.RoastedCoffee, id)

        if roasted_coffee is None:
            return {
                "status": False,
                "error": {
                    "code": 404,
                    "message": f"Roasted coffee with id `{id}` not found",
                },
            }

        for column in ["name", "roaster_id", "date_added", "date_removed"]:
            if (value := getattr(input, column)) is not MISSING:
                setattr(roasted_coffee, column, value)

        for input_attr, tag_name in [("profiles", "profile"), ("tasting", "tasting")]:
            if (tag_values := getattr(input, input_attr)) is not MISSING:
                # Reset tag type
                session.execute(
                    queries.RoastedCoffee().clear_tag(roasted_id=id, type="profile")
                )

                # Write new tags
                roasted_coffee.tags.extend(
                    [
                        models.RoastedCoffeeTag(type=tag_name, value=value)
                        for value in tag_values
                    ]
                )

        session.commit()
        session.refresh(roasted_coffee)

    return {"status": True, "roasted_coffee": roasted_coffee}


@mutation_type.field("roastedCoffeeTagAdd")
def resolve_roasted_coffee_tag_add(
    _, info: GraphQLResolveInfo, id: int, input: CoffeeTagInput
):
    Session = info.context["Session"]
    type = input.type

    if type not in SUPPORTED_TAG_TYPES:
        return {
            "status": False,
            "error": {"code": 400, "message": f"Unsupported tag type `{type}`"},
        }

    with Session() as session:
        session.add_all(
            [
                models.RoastedCoffeeTag(roasted_id=id, type=type, value=value)
                for value in input.values
            ]
        )

        session.commit()
        roasted_coffee = session.get(models.RoastedCoffee, id)

    return {"status": True, "roasted_coffee": roasted_coffee}


@mutation_type.field("roastedCoffeeTagDelete")
def resolve_roasted_coffee_tag_delete(
    _, info: GraphQLResolveInfo, id: int, input: CoffeeTagInput
):
    Session = info.context["Session"]

    if input.type not in SUPPORTED_TAG_TYPES:
        return {
            "status": False,
            "error": {"code": 400, "message": f"Unsupported tag type `{type}`"},
        }

    with Session() as session:
        session.execute(
            queries.RoastedCoffee().delete_tags(
                roasted_id=id, type=input.type, values=input.values
            )
        )

        session.commit()
        roasted_coffee = session.get(models.RoastedCoffee, id)

    return {"status": True, "roasted_coffee": roasted_coffee}


class CoffeeComponentInput(BaseModel):
    green_id: int | MISSING = MISSING
    origin_id: int | MISSING = MISSING
    process: str | None | MISSING = MISSING
    variety: str | None | MISSING = MISSING
    fraction: int | None | MISSING = MISSING
    date_added: datetime | None | MISSING = MISSING
    date_updated: datetime | None | MISSING = MISSING

    @model_validator(mode="after")
    def validate_coffee_components(self) -> Self:
        match (self.green_id, self.origin_id):
            case (int(), int()):
                raise ValueError(
                    "Too many parameters: only one of either `greenId` or `originId` can be specified."
                )
            case (g, o) if g is MISSING and o is MISSING:
                raise ValueError(
                    "Missing parameter: exactly one of either `greenId` or `originId` must be specified."
                )

        return self


coffee_component_input_type = InputType(
    "CoffeeComponentInput", lambda data: CoffeeComponentInput(**data)
)


@mutation_type.field("roastedCoffeeComponentAdd")
def resolve_roasted_coffee_component_add(
    _,
    info: GraphQLResolveInfo,
    id: int,
    input: CoffeeComponentInput,
):
    Session = info.context["Session"]

    input_data = input.model_dump()

    with Session() as session:
        roasted_coffee = session.get(models.RoastedCoffee, id)
        if roasted_coffee is None:
            return {
                "status": False,
                "error": {
                    "code": 404,
                    "message": f"Roasted coffee with id `{id}` not found",
                },
            }

        component_association = models.CoffeeComponent(
            roasted_id=id,
            fraction=input_data.get("fraction"),
        )

        if "date_added" in input_data:
            component_association.date_added = input_data["date_added"]
        if "date_updated" in input_data:
            component_association.date_updated = input_data["date_updated"]

        roasted_coffee.component_associations.append(component_association)

        if "green_id" in input_data:
            green_id = input_data["green_id"]

            green_coffee = session.get(models.GreenCoffee, green_id)

            if green_coffee is None:
                return {
                    "status": False,
                    "error": {
                        "code": 404,
                        "message": f"Green coffee with id `{green_id}` not found",
                    },
                }

            component_association.green_id = green_id

            session.commit()
            session.refresh(roasted_coffee)

        elif "origin_id" in input_data:
            origin_id = input_data["origin_id"]
            origin = session.get(models.Origin, origin_id)

            if origin is None:
                return {
                    "status": False,
                    "error": {
                        "code": 404,
                        "message": f"Origin with id `{origin_id}` not found",
                    },
                }

            component_association.origin_id = origin_id
            component_association.process = input_data.get("process")
            component_association.variety = input_data.get("variety")

            session.commit()
            session.refresh(roasted_coffee)

        return {
            "status": True,
            "roasted_coffee": roasted_coffee,
        }


@mutation_type.field("roastedCoffeeComponentDelete")
def resolve_roasted_coffee_component_delete(
    _, info: GraphQLResolveInfo, id: int, input: CoffeeComponentInput
):
    Session = info.context["Session"]

    input_data = input.model_dump()

    green_id = input_data.get("green_id")
    origin_id = input_data.get("origin_id")
    process = input_data.get("process")
    variety = input_data.get("variety")

    with Session() as session:
        roasted_coffee = session.get(models.RoastedCoffee, id)

        if roasted_coffee is None:
            return {
                "status": False,
                "error": {
                    "code": 404,
                    "message": f"Roasted coffee with id `{id}` not found",
                },
            }

        session.execute(
            queries.RoastedCoffee().delete_component(
                roasted_id=id,
                green_id=green_id,
                origin_id=origin_id,
                process=process,
                variety=variety,
            )
        )

        session.commit()
        roasted_coffee = session.get(models.RoastedCoffee, id)

    return {"status": True, "roasted_coffee": roasted_coffee}


@mutation_type.field("roastedCoffeeComponentUpdate")
def resolve_roasted_coffee_component_update(
    _, info: GraphQLResolveInfo, id: int, input: CoffeeComponentInput
):
    Session = info.context["Session"]

    input_data = input.model_dump()

    green_id = input_data.get("green_id")
    origin_id = input_data.get("origin_id")
    process = input_data.get("process")
    variety = input_data.get("variety")
    fraction = input_data.get("fraction")

    with Session() as session:
        roasted_coffee = session.get(models.RoastedCoffee, id)

        if roasted_coffee is None:
            return {
                "status": False,
                "error": {
                    "code": 404,
                    "message": f"Roasted coffee with id `{id}` not found",
                },
            }

        session.execute(
            queries.RoastedCoffee().update_component(
                roasted_id=id,
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
