from ariadne import ObjectType, InputType
from sqlalchemy import insert
from pydantic import ConfigDict, Json, MISSING
from typing import TYPE_CHECKING
from api.types import BaseModel

from .mutation import mutation_type, CoffeeTagInput
from db import models, queries

if TYPE_CHECKING:
    from graphql import GraphQLResolveInfo

SUPPORTED_TAG_TYPES = ["process", "variety", "tasting"]


class GreenCoffeeSource(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str | None = None
    source_type: str | None = None
    producer_name: str | None = None
    harvest_year: int | None = None
    country: models.Country
    origin: models.Origin
    community: str | None = None


green_coffee = ObjectType("GreenCoffee")


@green_coffee.field("source")
def resolve_green_coffee_source(
    green_coffee: models.GreenCoffee, info: GraphQLResolveInfo
) -> GreenCoffeeSource:
    Session = info.context["Session"]

    with Session() as session:
        origin = session.scalar(queries.GreenCoffee(green_coffee.id).get("origins"))
        country = origin.country

    return GreenCoffeeSource(
        name=green_coffee.source,
        source_type=green_coffee.source_type,
        producer_name=green_coffee.details.get("producer_name"),
        harvest_year=green_coffee.details.get("harvest_year"),
        country=country,
        origin=origin,
        community=green_coffee.community,
    )


@green_coffee.field("processes")
def resolve_green_coffee_processes(
    green_coffee: models.GreenCoffee, info: GraphQLResolveInfo
) -> list[str]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.GreenCoffee(green_coffee.id).get("processes")
        ).all()


@green_coffee.field("varieties")
def resolve_green_coffee_varieties(
    green_coffee: models.GreenCoffee, info: GraphQLResolveInfo
) -> list[str]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.GreenCoffee(green_coffee.id).get("varieties")
        ).all()


@green_coffee.field("tasting")
def resolve_green_coffee_tasting(
    green_coffee: models.GreenCoffee, info: GraphQLResolveInfo
) -> list[str]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.GreenCoffee(green_coffee.id).get("tasting")
        ).all()


@green_coffee.field("roasters")
def resolve_green_coffee_roasters(
    green_coffee: models.GreenCoffee, info: GraphQLResolveInfo
) -> list[models.Roaster]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.GreenCoffee(green_coffee.id).get("roasters")
        ).all()


@green_coffee.field("associations")
def resolve_green_coffee_associations(
    green_coffee: models.GreenCoffee, info: GraphQLResolveInfo
) -> list[models.CoffeeComponent]:
    Session = info.context["Session"]

    with Session() as session:
        return session.scalars(
            queries.GreenCoffee(green_coffee.id).get("associations")
        ).all()


class GreenCoffeeInput(BaseModel):
    name: str | MISSING = MISSING
    source: GreenCoffeeSourceInput | MISSING = MISSING
    details: Json[dict] | MISSING = MISSING
    processes: list[str] | MISSING = MISSING
    varieties: list[str] | MISSING = MISSING
    tasting: list[str] | MISSING = MISSING


class GreenCoffeeSourceInput(BaseModel):
    name: str | None | MISSING = MISSING
    type: str | None | MISSING = MISSING
    origin_id: int | None | MISSING = MISSING
    community: str | None | MISSING = MISSING
    details: Json[dict] | MISSING = MISSING


class GreenCoffeePatch(BaseModel):
    name: str | None | MISSING = MISSING
    source: str | None | MISSING = MISSING
    source_type: str | None | MISSING = MISSING
    origin_id: int | None | MISSING = MISSING
    community: str | None | MISSING = MISSING
    details: dict | MISSING = MISSING


def get_green_coffee_patch(input: GreenCoffeeInput) -> GreenCoffeePatch:
    patch = GreenCoffeePatch(name=input.name, details=input.details)

    if patch.details is MISSING:
        patch.details = {}

    if input.source is not MISSING:
        patch.source = input.source.name
        patch.source_type = input.source.type
        patch.origin_id = input.source.origin_id
        patch.community = input.source.community

        if input.source.details is not MISSING:
            patch.details.update(input.source.details)

    return patch


def get_green_coffee_tag_inputs(input: GreenCoffeeInput) -> list[CoffeeTagInput]:
    result = []

    if input.processes is not MISSING:
        result.append(CoffeeTagInput(type="process", values=input.processes))

    if input.varieties is not MISSING:
        result.append(CoffeeTagInput(type="variety", values=input.varieties))

    if input.tasting is not MISSING:
        result.append(CoffeeTagInput(type="tasting", values=input.tasting))

    return result


green_coffee_input_type = InputType(
    "GreenCoffeeInput", lambda data: GreenCoffeeInput(**data)
)


@mutation_type.field("greenCoffeeCreate")
def resolve_green_coffee_create(_, info: GraphQLResolveInfo, input: GreenCoffeeInput):
    Session = info.context["Session"]
    patch = get_green_coffee_patch(input)
    tags = get_green_coffee_tag_inputs(input)

    if patch.name is MISSING or not patch.name:
        return {
            "status": False,
            "error": {"code": 400, "message": "Missing required field `name`"},
        }

    try:
        with Session() as session:
            green_coffee = models.GreenCoffee(**patch.model_dump())

            for tag in tags:
                green_coffee.tags.extend(
                    [
                        models.GreenCoffeeTag(type=tag.type, value=value)
                        for value in tag.values
                    ]
                )

            session.add(green_coffee)

            session.commit()
            session.refresh(green_coffee)

        return {"status": True, "green_coffee": green_coffee}

    except:
        return {
            "status": False,
            "error": {"code": 500, "message": "Internal Server Error"},
        }


@mutation_type.field("greenCoffeeUpdate")
def resolve_green_coffee_update(
    _, info: GraphQLResolveInfo, id: int, input: GreenCoffeeInput
):
    Session = info.context["Session"]
    patch = get_green_coffee_patch(input)
    tags = get_green_coffee_tag_inputs(input)

    if not patch.name:
        return {
            "status": False,
            "error": {"code": 400, "message": "Cannot unset required field `name`"},
        }

    try:
        with Session() as session:
            green_coffee = session.get(models.GreenCoffee, id)

            if green_coffee is None:
                return {
                    "status": False,
                    "error": {
                        "code": 404,
                        "message": f"Green coffee with id `{id}` not found",
                    },
                }

            for key, value in patch.model_dump().items():
                setattr(green_coffee, key, value)

            # clear tag entries
            updated_tag_types = set([tag.type for tag in tags])

            for tag_type in updated_tag_types:
                session.execute(
                    queries.GreenCoffee().clear_tag(green_id=id, type=tag_type)
                )

            # write new tags
            for tag in tags:
                green_coffee.tags.extend(
                    [
                        models.GreenCoffeeTag(type=tag.type, value=value)
                        for value in tag.values
                    ]
                )

            session.commit()
            session.refresh(green_coffee)

    except:
        return {
            "status": False,
            "error": {"code": 500, "message": "Internal Server Error"},
        }

    return {"status": True, "green_coffee": green_coffee}


@mutation_type.field("greenCoffeeTagAdd")
def resolve_green_coffee_tag_add(
    _, info: GraphQLResolveInfo, id: int, input: CoffeeTagInput
):
    Session = info.context["Session"]

    if (type := input.type) not in SUPPORTED_TAG_TYPES:
        return {
            "status": False,
            "error": {"code": 400, "message": f"Unsupported tag type `{type}`"},
        }

    try:
        with Session() as session:
            session.add_all(
                [
                    models.GreenCoffeeTag(green_id=id, type=input.type, value=value)
                    for value in input.values
                ]
            )

            session.commit()
            green_coffee = session.get(models.GreenCoffee, id)

    except:
        return {
            "status": False,
            "error": {"code": 500, "message": "Internal Server Error"},
        }

    return {"status": True, "green_coffee": green_coffee}


@mutation_type.field("greenCoffeeTagDelete")
def resolve_green_coffee_tag_delete(
    _, info: GraphQLResolveInfo, id: int, input: CoffeeTagInput
):
    Session = info.context["Session"]

    if input.type not in SUPPORTED_TAG_TYPES:
        return {
            "status": False,
            "error": {"code": 400, "message": f"Unsupported tag type `{type}`"},
        }

    try:
        with Session() as session:
            session.execute(
                queries.GreenCoffee().delete_tags(
                    green_id=id, type=input.type, values=input.values
                )
            )

            session.commit()
            green_coffee = session.get(models.GreenCoffee, id)
    except:
        return {
            "status": False,
            "error": {"code": 500, "message": "Internal Server Error"},
        }

    return {"status": True, "green_coffee": green_coffee}
