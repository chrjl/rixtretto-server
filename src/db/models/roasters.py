from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from .base import Base
from ..utilities import normalized_text
from .utilities import representation

if TYPE_CHECKING:
    from .coffees import RoastedCoffee


class Roaster(Base):
    """Objects from the `roasters` table.

    Required attributes:
        name(str): name of the roaster
        country(str): 2-letter country code

    Relationships:
        coffees(list[RoastedCoffee])

    Optional attributes:
        city(str)
        state(str)
        equipment_brand(str)
        equipment_model(str)
        equipment_capacity(float): in kg

    JSON attributes:
        details: additional contact details (see contact.schema.json)

            {
                "website": "https://gget.com",
                "profiles": [
                    {
                        "network": "facebook",
                        "handle": "ggetla",
                        "url": "https://facebook.com/ggetla"
                    }
                ],
                "locations": [
                    {
                        "name": "Grand Central Market",
                        "type": "coffeebar",
                        "address": "317 S Broadway",
                        "city": "Los Angeles",
                        "state": "CA",
                        "zipcode": 90013
                    }
                ],
                "contacts": [
                    {
                        "name": "John Doe",
                        "title": "Head roaster",
                        "location": "Roastery",
                        "address": "123 Unknown",
                        "city": "Los Angeles",
                        "state": "CA",
                        "zipcode": 99999
                    }
                ]
            }
    """

    __tablename__ = "roasters"
    __table_args__ = {
        "comment": "Identity information of companies, people, or users that roast coffees."
    }

    id: Mapped[int] = mapped_column(primary_key=True)
    _name: Mapped[str] = mapped_column("name")
    _name_n: Mapped[str] = mapped_column(
        comment="`name` column normalized to remove case, accents, punctuation",
        default=lambda context: normalized_text(
            context.get_current_parameters()["name"]
        ),
    )

    @hybrid_property
    def name(self) -> str:
        return self._name

    @name.inplace.setter
    def name_setter(self, value: str):
        self._name_n = normalized_text(value)
        self._name = value

    city: Mapped[str | None]
    state: Mapped[str | None]
    country: Mapped[str] = mapped_column(
        String(length=2), comment="Two letter country code (ISO 3166-1 alpha-2)"
    )
    details: Mapped[dict] = mapped_column(
        nullable=True,
        server_default="{}",
        comment="Can include contact information, website, socials profiles, location details, etc.",
    )
    equipment_brand: Mapped[str | None]
    equipment_model: Mapped[str | None]
    equipment_capacity: Mapped[float | None] = mapped_column(
        comment="Size of the roasting machine in kg."
    )

    coffees: Mapped[list["RoastedCoffee"]] = relationship(back_populates="roaster")

    def __repr__(self):
        fields = {"id": getattr(self, "id", None), "name": getattr(self, "name", None)}

        return representation("Roaster", fields)
