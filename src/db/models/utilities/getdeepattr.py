from typing import Any
from sqlalchemy.orm.exc import DetachedInstanceError


def getdeepattr(obj: Any, attr: str, default: Any = None):
    result = obj

    for a in attr.split("."):
        try:
            if not hasattr(result, a):
                return default

            result = getattr(result, a)
        except DetachedInstanceError:
            return default

    return result
