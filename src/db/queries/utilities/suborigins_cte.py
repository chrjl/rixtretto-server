from sqlalchemy import BindParameter, Select, CTE, select
from db import models


def suborigins_cte(origin_ids: list[int] | BindParameter | Select) -> CTE:
    """Selectable CTE of all suborigin `origin_id`s of an origin (inclusive).

    Args:
        origin_id (int):
            Either the `id` from the `origins` table, or a bound parameter or
            selectable that provides it.

    Returns:
        sqlalchemy.CTE:
            Recursive CTE that, when selected, returns a single column of `id`s
            of the `origins` table.

    Usage:
        (
            select(Origin)
            .where(
                Origin.id.in_.select(suborigins_cte(bindparam("origin_id"))
            ),
            {"origin_id": 1},
        )

        suborigin_list = aliased(Origin, suborigins_cte(origin_id))
        select(suborigin_list)
    """
    cte = (
        select(models.Origin.id)
        .where(models.Origin.id.in_(origin_ids))
        .cte(recursive=True)
    )
    return cte.union_all(
        select(models.Origin.id).join(cte, cte.c.id == models.Origin.parent_id)
    )
