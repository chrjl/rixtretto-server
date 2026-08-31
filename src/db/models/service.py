from __future__ import annotations
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime

from .base import Base, BaseWithNormalizedName
from .utilities import representation, getdeepattr

if TYPE_CHECKING:
    from .roasters import Roaster


class Service(BaseWithNormalizedName):
    """
    Company/brand name of coffee service. Mapped to locations via association
    table.

    Required attributes:
        name(str)

    Optional attributes:
        roaster_id(int): if the retailer exclusively sells a single roaster

    Relationships:
        roaster(Roaster)
        locations(list[Location])
    """

    __tablename__ = "service"

    id: Mapped[int] = mapped_column(primary_key=True)
    roaster_id: Mapped[int] = mapped_column(
        ForeignKey("roasters.id"),
        nullable=True,
        comment="If service has an established relationship with a roaster.",
    )

    locations: Mapped[list["Location"]] = relationship(
        secondary="service_location_associations", viewonly=True
    )
    location_associations: Mapped[list["ServiceLocationAssociation"]] = relationship(
        back_populates="service"
    )
    roaster: Mapped["Roaster | None"] = relationship()
    menu_items: Mapped[list["MenuItem"]] = relationship(back_populates="service")

    def __repr__(self):
        return representation("Service", {"id": self.id, "name": self.name})


class Location(Base):
    """
    Specific locations of coffee service. Can be branches of a chain or a point
    of interest or event venue.

    Required attributes:
        retailer_id(int): the retailer that the location belongs to
        type(str): what type of location

    Optional attributes:
        name(str)
        address(str)
        city(str)
        state(str)
        country_id(str)

    Relationships:
        service_associations(list[ServiceLocationAssociation])
    """

    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str | None]
    address: Mapped[str | None]
    city: Mapped[str | None]
    state: Mapped[str | None]
    country_id: Mapped[str] = mapped_column(ForeignKey("countries.id"))

    service_associations: Mapped[list["ServiceLocationAssociation"]] = relationship(
        back_populates="location"
    )

    def __repr__(self):
        return representation(
            title="ServiceLocation",
            fields={
                "name": self.name,
                "city": self.city,
                "state": self.state,
                "country": self.country_id,
            },
        )


class ServiceLocationAssociation(Base):
    """
    Association table for mapping of locations to services.

    Required attributes:
        service_id(int, FK)
        location_id(int, FK)

    Optional attributes:
        address_detail(str): unit number, etc.
        neighborhood(str)
        name(str): the company's name for the specific location
        description(str): e.g. coffeeshop, popup, restaurant
        date_opened(datetime)
        date_closed(datetime)

    Relationships:
        location(Location)
        service(Service)
    """

    __tablename__ = "service_location_associations"

    service_id: Mapped[int] = mapped_column(ForeignKey("service.id"), primary_key=True)
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id"), primary_key=True
    )
    address_detail: Mapped[str | None]
    neighborhood: Mapped[str | None]
    name: Mapped[str | None] = mapped_column(
        comment="The company's name of the specific location or event"
    )

    description: Mapped[str | None] = mapped_column(
        comment="e.g. coffeeshop, popup, restaurant"
    )
    date_opened: Mapped[datetime | None]
    date_closed: Mapped[datetime | None]

    location: Mapped["Location"] = relationship(back_populates="service_associations")
    service: Mapped["Service"] = relationship(back_populates="location_associations")

    def __repr__(self):
        service = getdeepattr(self, "service.name")
        location = getdeepattr(self, "location.name")

        return representation(
            "ServiceLocationAssociation",
            fields={
                "service": service,
                "service_id": self.service_id if not service else None,
                "location": location,
                "location_id": self.location_id if not location else None,
            },
        )


class MenuItem(BaseWithNormalizedName):
    """
    Coffee drinks available in service.

    Required attributes:
        name(str) => sets => normalized_name(str, PK)
        service_id(PK, FK)

    Optional attributes:
        date_added(datetime)
        date_removed(datetime)
        details(JSON)

    Relationships:
        service(Service)
        variants(list[MenuItemVariant])
        ingredients(list[Ingredient]): secondary, through MenuItemIngredientAssociation
    """

    __tablename__ = "menu_items"
    __table_args__ = (PrimaryKeyConstraint("normalized_name", "service_id"),)

    service_id: Mapped[int] = mapped_column(
        ForeignKey("service.id"),
        comment="for specialty drinks limited to specific retailer",
    )

    date_added: Mapped[datetime | None]
    date_removed: Mapped[datetime | None] = mapped_column(
        comment="For when a specialty drink is a limited time offering."
    )
    details: Mapped[dict] = mapped_column(server_default="{}")

    service: Mapped[Service] = relationship(back_populates="menu_items")
    variants: Mapped[list["MenuItemVariant"]] = relationship()
    ingredients: Mapped[list["Ingredient"]] = relationship(
        secondary="menu_item_ingredient_associations",
        viewonly=True,
        back_populates="menu_items",
    )
    ingredient_associations: Mapped[list["MenuItemIngredientAssociation"]] = (
        relationship()
    )

    def __repr__(self):
        service = getdeepattr(self, "service.name")
        relationship_fields = {
            "service": service,
            "service_id": getattr(self, "service_id", None) if not service else None,
        }

        return representation(
            "MenuItem",
            {**relationship_fields, "name": self.name},
        )


class MenuItemVariant(Base):
    """
    Variants that a menu item is served in, e.g. iced, hot

    Required arguments:
        service_id(int, FK): references `menu_items.service_id`
        menu_item(int, FK): references `menu_items.normalized_name`
        variant(str)
    """

    __tablename__ = "menu_item_variants"
    __table_args__ = (
        ForeignKeyConstraint(
            ["service_id", "menu_item_pkey"],
            ["menu_items.service_id", "menu_items.normalized_name"],
        ),
    )

    service_id: Mapped[int] = mapped_column(primary_key=True)
    menu_item_pkey: Mapped[str] = mapped_column(primary_key=True)
    variant: Mapped[str] = mapped_column(primary_key=True)

    service: Mapped["Service"] = relationship(secondary="menu_items", viewonly=True)
    menu_item: Mapped["MenuItem"] = relationship(viewonly=True)


class Ingredient(BaseWithNormalizedName):
    """
    Ingredients used in making coffee drinks. Includes self-referential parent
    ingredient categories.

    Required attributes:
        name(str, PK)

    Optional attributes:
        parent_name(str, FK)

    Relationships:
        menu_items(list[MenuItem]): secondary through MenuItemIngredientAssociation
        parent(Ingredient)
        children(list[Ingredient])
    """

    __tablename__ = "menu_item_ingredients"
    __table_args__ = (PrimaryKeyConstraint("normalized_name"),)

    parent_name: Mapped[str | None] = mapped_column(
        ForeignKey(
            "menu_item_ingredients.normalized_name",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
    )

    parent: Mapped["Ingredient | None"] = relationship(
        back_populates="children",
        remote_side=lambda: Ingredient.normalized_name,
    )
    children: Mapped[list["Ingredient"]] = relationship(back_populates="parent")
    menu_items: Mapped[list["MenuItem"]] = relationship(
        secondary="menu_item_ingredient_associations",
        viewonly=True,
        back_populates="ingredients",
    )

    def __repr__(self):
        return representation("Ingredient", {"name": self.name})


class MenuItemIngredientAssociation(Base):
    """
    Association table for ingredients that go into product recipes.

    Required attributes:
        service_id(int, PK): references `menu_items.service_id`
        menu_item(str, PK): references `menu_items.normalized_name`
        ingredient_name(str, PK)

    Optional attributes:
        detail(JSON)
    """

    __tablename__ = "menu_item_ingredient_associations"
    __table_args__ = (
        ForeignKeyConstraint(
            ["service_id", "menu_item_pkey"],
            ["menu_items.service_id", "menu_items.normalized_name"],
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
    )

    service_id: Mapped[int] = mapped_column(primary_key=True)
    menu_item_pkey: Mapped[str] = mapped_column(primary_key=True)
    ingredient_pkey: Mapped[str] = mapped_column(
        ForeignKey(
            "menu_item_ingredients.normalized_name",
            onupdate="CASCADE",
            ondelete="RESTRICT",
        ),
        primary_key=True,
    )

    details: Mapped[dict] = mapped_column(server_default="{}")

    service: Mapped["Service"] = relationship(
        secondary="menu_items",
        viewonly=True,
    )
    menu_item: Mapped["MenuItem"] = relationship(viewonly=True)
    ingredient: Mapped["Ingredient"] = relationship(viewonly=True)

    def __repr__(self):
        fields = {
            "service": self.service.name,
            "menu_item": self.menu_item.name,
            "ingredient": self.ingredient,
        }
        return representation("MenuItemIngredientAssociation", fields)
