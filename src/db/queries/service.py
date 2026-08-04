from __future__ import annotations

from sqlalchemy import select, func, join, outerjoin

from db import models
from .base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self
    from sqlalchemy import Select, ColumnElement
    from .utilities.filters import LocationFilter


def location_filter_clauses(location_filter: LocationFilter) -> list[ColumnElement]:
    if not location_filter:
        return []
    
    filter_clauses: list[ColumnElement] = []

    if neighborhood := location_filter.get("neighborhood"):
        filter_clauses.append(
            func.lower(models.ServiceLocationAssociation.neighborhood).like(
                neighborhood.lower() + "%"
            ),
        )

    if address := location_filter.get("address"):
        filter_clauses.append(
            func.lower(models.Location.address).like("%" + address.lower() + "%"),
        )

    if city := location_filter.get("city"):
        filter_clauses.append(
            func.lower(models.Location.city).like(city.lower() + "%"),
        )

    if state := location_filter.get("state"):
        filter_clauses.append(
            func.lower(models.Location.state).like(state.lower() + "%"),
        )

    if country_id := location_filter.get("country_id"):
        filter_clauses.append(
            func.lower(models.Location.country_id).like(country_id.lower() + "%"),
        )

    if country_name := location_filter.get("country_name"):
        filter_clauses.append(
            func.lower(models.Country.name).like(country_name.lower() + "%"),
        )

    return filter_clauses


class Service(Base[models.Service]):
    def __init__(self, *ids: int):
        super().__init__(models.Service, *ids)

    def filter_by_location(self, location_filter: LocationFilter) -> Self:
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

        self._filters.extend(location_filter_clauses(location_filter))
        return self

    def locations(
        self, location_filter: LocationFilter = {}
    ) -> Select[tuple[models.Location]]:
        query = (
            select(models.Location)
            .join_from(models.Location, models.ServiceLocationAssociation)
            .join_from(models.Location, models.Country)
            .where(
                models.ServiceLocationAssociation.service_id.in_(self.select(["id"])),
                *location_filter_clauses(location_filter),
            )
        )

        return query

    def location_associations(self, location_filter: LocationFilter = {}):
        return (
            select(models.ServiceLocationAssociation)
            .join_from(models.ServiceLocationAssociation, models.Location)
            .join_from(models.Location, models.Country)
            .where(
                models.ServiceLocationAssociation.service_id.in_(self.select(["id"])),
                *location_filter_clauses(location_filter),
            )
        )
