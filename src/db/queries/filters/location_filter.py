from api.types import BaseModel
from pydantic import MISSING


class LocationFilter(BaseModel):
    neighborhood: str | MISSING = MISSING
    city: str | MISSING = MISSING
    state: str | MISSING = MISSING
    country_id: str | MISSING = MISSING
