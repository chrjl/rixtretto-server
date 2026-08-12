from __future__ import annotations

from sqlalchemy import select
from db import models
from .utilities.filters import name_filter_clauses

from typing import TYPE_CHECKING, TypeVar, Type, Generic, Sequence

if TYPE_CHECKING:
    from typing import Self
    from sqlalchemy import ColumnElement, Select, Join
    from .utilities.filters import NameFilter


T = TypeVar("T", bound=models.Base)


class Base(Generic[T]):
    def __init__(
        self,
        model: Type[T],
        *ids: tuple[str | int] | str | int,
        pkey: str = "id",
    ):
        self._model = model
        self._filters: list[ColumnElement] = []
        self._joins: list[Join] = []
        self._pkey: str = pkey

        if ids:
            self.filter_by_pkey(ids, pkey=pkey)

    def select(
        self,
        columns: list[str] | None = None,
    ) -> Select[tuple[T]]:
        if columns is None:
            return (
                select(self._model)
                .group_by(getattr(self._model, self._pkey))
                .select_from(self._model, *self._joins)
                .where(*self._filters)
            )

        return (
            select(*[getattr(self._model, c) for c in columns])
            .group_by(getattr(self._model, self._pkey))
            .select_from(self._model, *self._joins)
            .where(*self._filters)
        )

    def get(self, attribute: str, cols: list[str] | None = None):
        if cols is not None:
            return getattr(self, attribute)(cols)

        return getattr(self, attribute)()

    def filter_by_pkey(
        self,
        ids: Sequence[tuple[str | int] | str | int] | Select[tuple[T]],
        pkey: str = "id",
    ) -> Self:
        self._filters.append(getattr(self._model, pkey).in_(ids))

        return self

    def filter_by_name(
        self,
        filter: NameFilter,
        name_column: str = "normalized_name",
        normalize: bool = True,
    ) -> Self:
        self._filters.extend(
            name_filter_clauses(
                filter,
                model=self._model,
                name_column=name_column,
                normalize=normalize,
            )
        )

        return self
