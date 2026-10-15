import json
import pydantic
import ariadne
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
        return super().__init__(name, errors_handled(out_type), *args)
