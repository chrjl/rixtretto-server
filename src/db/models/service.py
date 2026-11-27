from sqlalchemy import ForeignKey, PrimaryKeyConstraint, ForeignKeyConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime

from .base import Base, BaseWithNormalizedName
from .utilities import representation, getdeepattr

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .roasters import Roaster
    from .identities import Identity, Location
    from db.models import RoastedCoffee


class Service(Base):
    """
    Company/brand name of coffee service.

    Required attributes:
        id: PK, FK (identities.id)

    Relationships:
        identity(Identity)
        locations(list[Location]): via association
        roasted_coffees(list[RoastedCoffee]): list of roasted_coffees served
        coffee_associations(list[RoastedCoffeeAssociation])
    """

    __tablename__ = "service"

    id: Mapped[int] = mapped_column(ForeignKey("identities.id"), primary_key=True)

    identity: Mapped[Identity] = relationship()
    locations: Mapped[list["Location"]] = relationship(secondary="identities")
    menu_items: Mapped[list["MenuItem"]] = relationship(back_populates="service")
    roasted_coffees: Mapped[list["RoastedCoffee"]] = relationship(
        secondary="service_coffee_associations",
        overlaps="coffee_associations, roasted_coffee, service",
    )
    coffee_associations: Mapped[list["ServiceCoffeeAssociation"]] = relationship(
        back_populates="service"
    )

    def __repr__(self):
        return representation("Service", {"id": self.id, "name": "name"})


class ServiceCoffeeAssociation(Base):
    """
    Association table for mapping of roasted coffees to services.

    Required attributes:
        service_id(int, FK)
        roasted_coffee_id(int, FK)

    Optional attributes:
        details(JSON)
        date_opened(datetime)
        date_closed(datetime)

    Relationships:
        roasted_coffee(RoastedCoffee)
        service(Service)
    """

    __tablename__ = "service_coffee_associations"

    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(
        ForeignKey("service.id"), onupdate="CASCADE"
    )
    roasted_coffee_id: Mapped[int] = mapped_column(
        ForeignKey("roasted_coffees.id"), onupdate="CASCADE"
    )

    description: Mapped[str | None] = mapped_column(
        comment="e.g. coffeeshop, popup, restaurant"
    )
    details: Mapped[dict] = mapped_column(server_default="{}")
    date_added: Mapped[datetime | None]
    date_removed: Mapped[datetime | None]

    roasted_coffee: Mapped["RoastedCoffee"] = relationship()
    service: Mapped["Service"] = relationship(back_populates="coffee_associations")

    def __repr__(self):
        service = getdeepattr(self, "service.name")
        roasted_coffee = getdeepattr(self, "roasted_coffee.name")

        return representation(
            "ServiceCoffeeAssociation",
            fields={
                "service": service,
                "service_id": self.service_id if not service else None,
                "roasted_coffee": roasted_coffee,
                "roasted_coffee_id": (
                    self.roasted_coffee_id if not roasted_coffee else None
                ),
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
        onupdate="CASCADE",
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
            onupdate="CASCADE",
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
            "service": "name", #!TODO
            "menu_item": self.menu_item.name,
            "ingredient": self.ingredient,
        }
        return representation("MenuItemIngredientAssociation", fields)
