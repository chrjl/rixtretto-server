from typing import Any


def representation(title: str, fields: dict[str, Any]) -> str:
    items = []

    for field, value in fields.items():
        try:
            if type(value) == str:
                items.append(f'{field}="{value}"')
            elif value is not None:
                items.append(f"{field}={str(value)}")
        except AttributeError or KeyError:
            pass

    return f"{title}({", ".join(items)})"
