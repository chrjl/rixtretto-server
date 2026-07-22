from sqlalchemy import JSON
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.mutable import MutableList, MutableDict


class Base(DeclarativeBase):
    type_annotation_map = {
        list[str]: MutableList.as_mutable(JSON),
        list[dict]: MutableList.as_mutable(JSON),
        dict: MutableDict.as_mutable(JSON),
    }
