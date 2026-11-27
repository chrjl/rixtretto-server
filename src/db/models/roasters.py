from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .utilities import representation

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .identities import Location
    from .coffees import RoastedCoffee


class Roaster(Base):
    """Objects from the `roasters` table.

    Required attributes:
        id: PK, FK (identities.id)
        name(str): name of the roaster

    Relationships:
        identity(Identity)
        locations(list[Location]): via association
        coffees(list[RoastedCoffee])

    """

    __tablename__ = "roasters"
    __table_args__ = {
        "comment": "Identity information of companies, people, or users that roast coffees."
    }

    id: Mapped[int] = mapped_column(ForeignKey("identities.id"), primary_key=True)
    equipment_brand: Mapped[str | None]
    equipment_model: Mapped[str | None]
    equipment_capacity: Mapped[float | None] = mapped_column(
        comment="Size of the roasting machine in kg."
    )

    locations: Mapped[list[Location]] = relationship(secondary="identities")
    coffees: Mapped[list["RoastedCoffee"]] = relationship(back_populates="roaster")

    def __repr__(self):
        fields = {"id": getattr(self, "id", None), "name": getattr(self, "name", None)}

        return representation("Roaster", fields)
