from sqlalchemy import JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.mutable import MutableList, MutableDict
from sqlalchemy.ext.hybrid import hybrid_property

from ..utilities import normalized_text


class Base(DeclarativeBase):
    type_annotation_map = {
        list[str]: MutableList.as_mutable(JSON),
        list[dict]: MutableList.as_mutable(JSON),
        dict: MutableDict.as_mutable(JSON),
    }


class BaseWithNormalizedName(Base):
    __abstract__ = True

    _name: Mapped[str] = mapped_column("name")
    normalized_name: Mapped[str] = mapped_column(
        comment="`name` column normalized to remove case, accents, punctuation",
        default=lambda context: normalized_text(
            context.get_current_parameters()["name"],
            remove_spaces=True,
        ),
    )

    @hybrid_property
    def name(self) -> str:
        return self._name

    @name.inplace.setter
    def name_setter(self, value: str) -> None:
        self._name = value
        self.normalized_name = normalized_text(value)
