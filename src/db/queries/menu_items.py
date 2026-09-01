from sqlalchemy import select

from db import models
from .base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy import Select
    from typing import Self


class MenuItem(Base[models.MenuItem]):
    def __init__(self, *ids):
        super().__init__(models.MenuItem, *ids, pkey="normalized_name")

    def filter_by_service(self, ids: list[int] | Select[tuple[models.Service]]) -> Self:
        self._filters.append(models.MenuItem.service_id.in_(ids))
        return self

    def variants(self):
        query = select(models.MenuItemVariant.variant).where(
            models.MenuItemVariant.menu_item.in_(self.select(["normalized_name"]))
        )

        return query
