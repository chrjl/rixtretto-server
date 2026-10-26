from sqlalchemy import select, func, join, outerjoin

from db import models
from .base import Base
from db.queries.filters import LocationFilter
from db.utilities import normalized_text

from pydantic import MISSING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self
    from sqlalchemy import Select, ColumnElement


def location_filter_clauses(location_filter: LocationFilter) -> list[ColumnElement]:
    if not location_filter:
        return []

    filter_clauses: list[ColumnElement] = []

    if (neighborhood := location_filter.neighborhood) is not MISSING:
        filter_clauses.append(
            func.lower(models.ServiceLocationAssociation.neighborhood).like(
                normalized_text(neighborhood, remove_spaces=False) + "%"
            ),
        )

    if (city := location_filter.city) is not MISSING:
        filter_clauses.append(
            func.lower(models.Location.city).like(
                normalized_text(city, remove_spaces=False) + "%"
            ),
        )

    if (state := location_filter.state) is not MISSING:
        filter_clauses.append(
            func.lower(models.Location.state).like(
                normalized_text(state, remove_spaces=False) + "%"
            ),
        )

    if (country_id := location_filter.country_id) is not MISSING:
        filter_clauses.append(
            func.lower(models.Location.country_id).like(
                normalized_text(country_id, remove_spaces=False) + "%"
            ),
        )

    return filter_clauses


class Service(Base[models.Service]):
    def __init__(self, *ids: int):
        super().__init__(models.Service, *ids)

    def filter_by_location(self, location_filter) -> Self:
        if not location_filter:
            return self

        self._joins.append(
            join(
                models.Service,
                models.ServiceLocationAssociation,
                models.Service.id == models.ServiceLocationAssociation.service_id,
            )
            .join(
                models.Location,
                models.Location.id == models.ServiceLocationAssociation.location_id,
            )
            .join(
                models.Country,
                models.Location.country_id == models.Country.id,
            )
        )

        self._filters.extend(location_filter_clauses(LocationFilter(**location_filter)))
        return self

    def locations(self, location_filter={}) -> Select[models.Location]:
        return (
            select(models.Location)
            .join_from(models.Location, models.ServiceLocationAssociation)
            .join_from(models.Location, models.Country)
            .where(
                models.ServiceLocationAssociation.service_id.in_(self.select(["id"])),
                *location_filter_clauses(LocationFilter(**location_filter)),
            )
        )

    def location_associations(self, location_filter={}):
        return (
            select(models.ServiceLocationAssociation)
            .join_from(models.ServiceLocationAssociation, models.Location)
            .join_from(models.Location, models.Country)
            .where(
                models.ServiceLocationAssociation.service_id.in_(self.select(["id"])),
                *location_filter_clauses(LocationFilter(**location_filter)),
            )
        )
