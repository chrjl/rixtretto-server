import json
import pydantic
import ariadne
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, DataError
from typing import Callable
from graphql import GraphQLError


class BaseModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="forbid")


def handle_validation_errors(f):
    def _handle_validation_errors(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except pydantic.ValidationError as exc:
            raise GraphQLError(
                "Validation errors",
                extensions={
                    "details": json.loads(
                        exc.json(include_context=False, include_url=False)
                    ),
                },
            )

    return _handle_validation_errors


class InputType(ariadne.InputType):
    def __init__(self, name, out_type, *args):
        return super().__init__(name, handle_validation_errors(out_type), *args)


def handle_resolver_errors(resolver: Callable) -> Callable:
    def wrapped_resolver(*args, **kwargs):
        try:
            return resolver(*args, **kwargs)

        except ValueError as exc:
            return {
                "status": False,
                "error": {"code": 400, "message": exc.args[0]},
            }

        except LookupError as exc:
            return {
                "status": False,
                "error": {"code": 404, "message": exc.args[0]},
            }

        except (IntegrityError, DataError):
            return {
                "status": False,
                "error": {"code": 400, "message": "Unprocessable data"},
            }

        except SQLAlchemyError:
            return {
                "status": False,
                "error": {"code": 500, "message": "DB Error"},
            }

    return wrapped_resolver


class ObjectType(ariadne.ObjectType):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def field(self, name) -> Callable:
        def _field(resolver):
            wrapped_resolver = handle_resolver_errors(resolver)
            return super(ObjectType, self).field(name)(wrapped_resolver)

        return _field


class MutationType(ariadne.MutationType):
    def __init__(self, *args, **kwargs):
        return super().__init__(*args, **kwargs)

    def field(self, name) -> Callable:
        def _field(resolver):
            wrapped_resolver = handle_resolver_errors(resolver)
            return super(MutationType, self).field(name)(wrapped_resolver)

        return _field
