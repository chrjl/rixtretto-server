from sqlalchemy import func, join

from db import models
from .base import Base
from db.queries.filters import LocationFilter
from db.utilities import normalized_text

from pydantic import MISSING
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self
    from sqlalchemy import ColumnElement


def location_filter_clauses(
    model, location_filter: LocationFilter
) -> list[ColumnElement]:
    filter_clauses: list[ColumnElement] = []

    if (neighborhood := location_filter.neighborhood) is not MISSING:
        filter_clauses.append(
            func.lower(model.neighborhood).like(
                normalized_text(neighborhood, remove_spaces=False) + "%"
            ),
        )

    if (city := location_filter.city) is not MISSING:
        filter_clauses.append(
            func.lower(model.city).like(
                normalized_text(city, remove_spaces=False) + "%"
            ),
        )

    if (state := location_filter.state) is not MISSING:
        filter_clauses.append(
            func.lower(model.state).like(
                normalized_text(state, remove_spaces=False) + "%"
            ),
        )

    if (country_id := location_filter.country_id) is not MISSING:
        filter_clauses.append(
            func.lower(model.country).like(
                normalized_text(country_id, remove_spaces=False) + "%"
            ),
        )

    return filter_clauses


class Roaster(Base[models.Roaster]):
    def __init__(self, *ids: int):
        super().__init__(models.Roaster, *ids)

    def filter_by_location(self, location_filter) -> Self:
        self._joins.append(
            join(
                models.Roaster,
                models.Country,
                models.Roaster.country == models.Country.id,
            )
        )

        self._filters.extend(
            location_filter_clauses(models.Roaster, LocationFilter(**location_filter))
        )

        return self
