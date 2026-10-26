from api.types import BaseModel
from pydantic import MISSING
from sqlalchemy import ColumnElement, func
from db.utilities import normalized_text


class NameFilter(BaseModel):
    starts_with: str | MISSING = MISSING
    contains: str | MISSING = MISSING


def name_filter_clauses(
    model,
    name_filter: NameFilter,
    name_column: str = "normalized_name",
    normalize: bool = True,
) -> list[ColumnElement]:
    if filter is None:
        return []

    filter_clauses: list[ColumnElement] = []

    if (starts_with := name_filter.starts_with) is not MISSING:
        if normalize:
            filter_clauses.append(
                func.lower(getattr(model, name_column)).like(
                    (f"{normalized_text(starts_with)}%")
                )
            )
        else:
            filter_clauses.append(
                func.lower(getattr(model, name_column)).like(
                    (f"{starts_with.lower()}%")
                )
            )

    if (contains := name_filter.contains) is not MISSING:
        if normalize:
            filter_clauses.append(
                func.lower(getattr(model, name_column)).like(
                    (f"%{normalized_text(contains)}%")
                )
            )
        else:
            filter_clauses.append(
                func.lower(getattr(model, name_column)).like((f"%{contains.lower()}%"))
            )

    return filter_clauses
