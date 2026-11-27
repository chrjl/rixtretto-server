from .base import Base, BaseWithNormalizedName

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .utilities import representation, getdeepattr

from datetime import datetime


class Identity(BaseWithNormalizedName):
    """Coffee-related identities to be associated with `roasters` and `service`.

    Required attributes:
        name(str)
        country_id(str, FK): 2-letter country code
        user_id(str, FK): #TODO

    Optional attributes:
        city(str): of founding, or that which identity is most closely
        identified with.

    Relationships:
        locations(list[Location]): back-populates `locations.identity_id`

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

    __tablename__ = "identities"
    __table_args__ = {
        "comment": "List of identities of coffee-related companies or people."
    }

    id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str | None]
    country_id: Mapped[str] = mapped_column(ForeignKey("countries.id"))
    details: Mapped[dict] = mapped_column(
        nullable=True,
        server_default="{}",
        comment="Can include contact information, website, socials profiles, location details, etc.",
    )

    locations: Mapped[list[Location]] = relationship(back_populates="identity")

    def __repr__(self):
        return representation("Identity", {"id": self.id, "name": self.name})


class Location(Base):
    """
    Specific locations of coffee service. Can be branches of a chain or a point
    of interest or event venue.

    Required attributes:
        identity_id(int): the identity that the location belongs to
        type(str): type of location (e.g. roastery, coffeeshop, popup, restaurant)

    Optional attributes:
        name(str)
        address(str)
        address_detail(str): unit number, etc.
        neighborhood(str)
        city(str)
        country_id(str)
        date_opened(datetime)
        date_closed(datetime)
        details(JSON)

    Relationships:
        identity(Identity): backpopulates `identity.locations`
    """

    __tablename__ = "location_associations"

    id: Mapped[int] = mapped_column(primary_key=True)
    identity_id: Mapped[int] = mapped_column(ForeignKey("identities.id"))
    type: Mapped[str | None] = mapped_column(
        comment="type of location (e.g. roastery, coffeeshop, popup, restaurant)"
    )

    name: Mapped[str | None]
    address: Mapped[str | None]
    address_detail: Mapped[str | None]
    neighborhood: Mapped[str | None]
    city: Mapped[str | None]
    country_id: Mapped[str] = mapped_column(ForeignKey("countries.id"))

    date_opened: Mapped[datetime | None]
    date_closed: Mapped[datetime | None]

    details: Mapped[dict]

    identity: Mapped[Identity] = relationship(back_populates="locations")

    def __repr__(self):
        identity_name = getdeepattr(self, "identity.name", None)

        fields = {
            "id": self.id,
            "identity": identity_name,
            "identity_id": (
                getattr(self, "identity_id", None) if not identity_name else None
            ),
            "type": getattr(self, "type", None),
            "name": getattr(self, "name", None),
        }

        return representation(title="Location", fields=fields)
