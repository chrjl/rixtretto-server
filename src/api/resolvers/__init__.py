from .query import query
from .origin import origin
from .country import country
from .roaster import roaster, roaster_input_type
from .green_coffee import (
    green_coffee,
    green_coffee_input_type,
)
from .roasted_coffee import (
    roasted_coffee,
    roasted_coffee_input_type,
    coffee_component_input_type,
)
from .coffee_component import component_association
from .coffee_service import coffee_service
from .menu_item import menu_item
from .ingredient import ingredient

from .mutation import mutation_type, coffee_tag_input_type

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

input_types = [
    roaster_input_type,
    green_coffee_input_type,
    coffee_tag_input_type,
    roasted_coffee_input_type,
    coffee_component_input_type,
]
