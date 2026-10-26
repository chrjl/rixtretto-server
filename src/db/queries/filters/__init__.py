from api.types import BaseModel
from pydantic import MISSING
from .name_filter import NameFilter, name_filter_clauses
from .location_filter import LocationFilter
from .coffee_filter import CoffeeFilter, coffee_filter_clauses


class Filter(CoffeeFilter):
    name: NameFilter | MISSING = MISSING
    location: LocationFilter | MISSING = MISSING
    menu: NameFilter | MISSING = MISSING
