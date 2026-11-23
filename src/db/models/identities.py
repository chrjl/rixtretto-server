from .base import BaseWithNormalizedName

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .utilities import representation


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
        roaster: back-populates `roaster.id`
        service: back-populates `service.id`
        locations: back-populates `locations.id`

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

    def __repr__(self):
        return representation("Identity", {"id": self.id, "name": self.name})
