import json
import pydantic
from typing import TypedDict, Required

from db import models


class BaseModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")
