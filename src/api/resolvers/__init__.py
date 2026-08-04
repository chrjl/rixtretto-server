from .query import query
from .mutation import mutation_type
from .origin import origin
from .country import country
from .roaster import roaster
from .green_coffee import green_coffee
from .roasted_coffee import roasted_coffee
from .coffee_component import component_association
from .coffee_service import coffee_service

types = [
    query,
    mutation_type,
    origin,
    country,
    roaster,
    green_coffee,
    roasted_coffee,
    component_association,
    coffee_service,
]
