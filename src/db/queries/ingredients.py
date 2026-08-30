from sqlalchemy import select

from db import models
from .base import Base
from .utilities.filters import NameFilter


class Ingredient(Base[models.Ingredient]):
    def __init__(self, *ids: str):
        super().__init__(models.Ingredient, *ids, pkey="normalized_name")

    def descendants_cte(self, inclusive: bool = False):
        cte = (
            (
                select(getattr(models.Ingredient, self._pkey))
                .where(models.Ingredient.name.in_(self.select([self._pkey])))
                .cte(recursive=True)
            )
            if inclusive
            else (
                select(getattr(models.Ingredient, self._pkey))
                .where(models.Ingredient.parent_name.in_(self.select([self._pkey])))
                .cte(recursive=True)
            )
        )

        cte = cte.union(
            select(getattr(models.Ingredient, self._pkey)).join(
                cte, cte.c.normalized_name == models.Ingredient.parent_name
            )
        )

        return cte

    def descendants(self):
        return select(models.Ingredient).where(
            models.Ingredient.normalized_name.in_(
                select(self.descendants_cte(inclusive=False))
            )
        )

    def ancestors_cte(self, inclusive=False):
        cte = (
            (
                select(models.Ingredient.name)
                .where(
                    getattr(models.Ingredient, self._pkey).in_(
                        self.select([self._pkey])
                    )
                )
                .cte(recursive=True)
            )
            if inclusive
            else (
                select(models.Ingredient.parent_name)
                .where(
                    getattr(models.Ingredient, self._pkey).in_(
                        self.select([self._pkey])
                    )
                )
                .cte(recursive=True)
            )
        )

        cte = cte.union(
            select(models.Ingredient.parent_name)
            .join(cte, cte.c.parent_name == models.Ingredient.normalized_name)
            .where(models.Ingredient.parent_name.is_not(None))
        )

        return cte

    def ancestors(self):
        return select(models.Ingredient).where(
            models.Ingredient.normalized_name.in_(select(self.ancestors_cte()))
        )

    def menu_items(self):
        return (
            select(models.MenuItem)
            .join(models.MenuItemIngredientAssociation)
            .where(
                models.MenuItemIngredientAssociation.ingredient_pkey.in_(
                    select(self.descendants_cte(inclusive=True))
                )
            )
        )
