from ariadne import ObjectType

from db.queries.utilities.filters import Filter, LocationFilter
from db import models, queries

coffee_service = ObjectType("CoffeeService")


@coffee_service.field("roaster")
def resolve_roaster(service: models.Service, info):
    roaster_id = service.roaster_id

    if roaster_id is None:
        return None

    Session = info.context["Session"]

    with Session() as session:
        return session.get(models.Roaster, service.roaster_id)


@coffee_service.field("locations")
def resolve_locations(service: models.Service, info):
    Session = info.context["Session"]

    filter: Filter = info.context.get("_filter", {})
    location_filter: LocationFilter = filter.get("location", {})
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
