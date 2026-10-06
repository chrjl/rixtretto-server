from ariadne import MutationType, InputType
from pydantic import StringConstraints, MISSING
from typing import Annotated
from api.types import BaseModel

mutation_type = MutationType()


class Error(BaseModel):
    code: int
    message: str


class LocationInput(BaseModel):
    city: str | None | MISSING = MISSING
    state: str | None | MISSING = MISSING
    country_id: (
        Annotated[str, StringConstraints(min_length=2, max_length=2)] | MISSING
    ) = MISSING


class CoffeeTagInput(BaseModel):
    type: str
    values: list[str]


coffee_tag_input_type = InputType("CoffeeTagInput", lambda data: CoffeeTagInput(**data))
