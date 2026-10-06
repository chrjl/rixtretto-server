from .query import query
from .origin import origin
from .country import country
from .roaster import roaster
from .green_coffee import green_coffee
from .roasted_coffee import roasted_coffee
from .coffee_component import component_association
from .coffee_service import coffee_service
from .menu_item import menu_item
from .ingredient import ingredient

from .mutation import mutation_type

object_types = [
    query,
    origin,
    country,
    roaster,
    green_coffee,
    roasted_coffee,
    component_association,
    coffee_service,
    menu_item,
    ingredient,
]

input_types = []
]
