from pydantic import MISSING
from api.types import BaseModel, ObjectType, InputType
from db.queries.filters import Filter, LocationFilter, NameFilter
from db import models, queries
from .mutation import mutation_type

coffee_service = ObjectType("CoffeeService")

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graphql import GraphQLResolveInfo


@coffee_service.field("roaster")
def resolve_roaster(service: models.Service, info):
    roaster_id = service.roaster_id

    if roaster_id is None:
        return None

    Session = info.context["Session"]

    with Session() as session:
        return session.get(models.Roaster, service.roaster_id)


@coffee_service.field("locations")
def resolve_locations(service: models.Service, info: GraphQLResolveInfo):
    Session = info.context["Session"]

    filter = info.context.get("_filter", {})
    location_filter = filter.get("location", {})
    query = queries.Service(service.id).location_associations(location_filter)

    with Session() as session:
        location_associations = session.scalars(query).all()

        result = [
            {
                "name": row.name,
                "description": row.description,
                "location": {
                    "name": row.location.name,
                    "address": row.location.address,
                    "address_detail": row.address_detail,
                    "neighborhood": row.neighborhood,
                    "city": row.location.city,
                    "state": row.location.state,
                    "country": session.scalars(
                        queries.Country(row.location.country_id).select()
                    ).one(),
                },
                "date_opened": row.date_opened,
                "date_closed": row.date_closed,
            }
            for row in location_associations
        ]

        return result


@coffee_service.field("menu")
def resolve_menu_items(service: models.Service, info: GraphQLResolveInfo):
    Session = info.context["Session"]
    filter = info.context.get("_filter", {})
    menu_filter = filter.get("menu", {})

    with Session() as session:
        if menu_filter:
            return session.scalars(
                queries.MenuItem()
                .filter_by_service([service.id])
                .filter_by_name(menu_filter)
                .select()
            ).all()

        session.add(service)
        return service.menu_items


@coffee_service.field("coffees")
def resolve_coffees(
    service: models.Service, info: GraphQLResolveInfo
) -> list[models.RoastedCoffee]:
    Session = info.context["Session"]

    with Session() as session:
        session.add(service)
        return service.roasted_coffees


@coffee_service.field("origins")
def resolve_origins(
    service: models.Service, info: GraphQLResolveInfo
) -> list[models.Origin]:
    Session = info.context["Session"]

    with Session() as session:
        session.add(service)

        result = session.scalars(
            queries.RoastedCoffee(
                *[coffee.id for coffee in service.roasted_coffees]
            ).get("origins")
        ).all()

        return result


@coffee_service.field("processes")
def resolve_processes(service: models.Service, info: GraphQLResolveInfo) -> list[str]:
    Session = info.context["Session"]

    with Session() as session:
        session.add(service)

        return session.scalars(
            queries.RoastedCoffee(
                *[coffee.id for coffee in service.roasted_coffees]
            ).get("processes")
        ).all()


@coffee_service.field("varieties")
def resolve_varieties(service: models.Service, info: GraphQLResolveInfo) -> list[str]:
    Session = info.context["Session"]

    with Session() as session:
        session.add(service)

        return session.scalars(
            queries.RoastedCoffee(
                *[coffee.id for coffee in service.roasted_coffees]
            ).get("varieties")
        ).all()


class CoffeeServiceInput(BaseModel):
    name: str | MISSING = MISSING
    coffee_ids: list[int] | MISSING = MISSING
    location_ids: list[int] | MISSING = MISSING


coffee_service_input_type = InputType(
    "CoffeeServiceInput", lambda data: CoffeeServiceInput(**data)
)


@mutation_type.field("coffeeServiceCreate")
def resolve_coffee_service_create(
    _, info: GraphQLResolveInfo, input: CoffeeServiceInput
):
    Session = info.context["Session"]

    name = input.name
    # coffee_ids = input.coffee_ids
    # location_ids = input.location_ids

    if name is MISSING:
        raise ValueError("Missing required field `name`")

    service = models.Service(name=name)

    with Session() as session:
        session.add(service)
        session.commit()

        session.refresh(service)

    return {"status": True, "service": service}


@mutation_type.field("coffeeServiceUpdate")
def resolve_coffee_service_update(
    _, info: GraphQLResolveInfo, id: int, input: CoffeeServiceInput
):
    Session = info.context["Session"]

    with Session() as session:
        service = session.get(models.Service, id)

        for key, value in input.model_dump().items():
            setattr(service, key, value)

        session.commit()
        session.refresh(service)

    return {"status": True, "service": service}
