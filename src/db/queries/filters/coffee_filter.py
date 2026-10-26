from api.types import BaseModel
from pydantic import MISSING
from sqlalchemy import or_, and_, func, select

from db import models
from db.utilities import normalized_text
from db.queries.subqueries.suborigins_cte import suborigins_cte

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy import ColumnElement


class CoffeeFilter(BaseModel):
    origins: list[int] | MISSING = MISSING
    profiles: list[str] | MISSING = MISSING
    processes: list[str] | MISSING = MISSING
    varieties: list[str] | MISSING = MISSING
    tasting: list[str] | MISSING = MISSING


def coffee_filter_clauses(filter: CoffeeFilter) -> list[ColumnElement]:
    filter_clauses: list[ColumnElement] = []

    if (origins := filter.origins) is not MISSING:
        filter_clauses.append(
            or_(
                models.GreenCoffee.origin_id.in_(select(suborigins_cte(origins))),
                models.CoffeeComponent.origin_id.in_(select(suborigins_cte(origins))),
            )
        )

    if (profiles := filter.profiles) is not MISSING:
        filter_clauses.append(
            and_(
                models.RoastedCoffeeTag.type == "profile",
                func.lower(models.RoastedCoffeeTag.value).in_(
                    [normalized_text(p) for p in profiles]
                ),
            )
        )

    if (processes := filter.processes) is not MISSING:
        filter_clauses.append(
            or_(
                and_(
                    models.GreenCoffeeTag.type == "process",
                    func.lower(models.GreenCoffeeTag.value).in_(
                        [normalized_text(p) for p in processes]
                    ),
                ),
                models.CoffeeComponent.process.in_(processes),
            )
        )

    if (varieties := filter.varieties) is not MISSING:
        filter_clauses.append(
            and_(
                models.GreenCoffeeTag.type == "variety",
                func.lower(models.GreenCoffeeTag.value).in_(
                    [normalized_text(v) for v in varieties]
                ),
            ),
        )

    return filter_clauses
