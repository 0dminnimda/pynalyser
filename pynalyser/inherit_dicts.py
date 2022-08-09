from typing import Any, Dict, Mapping, Set, Tuple, cast


DICTS = "_dicts_to_inherit"


class DictNotFoundError(AttributeError):
    message_template = (
        "attribute '{attribute}' was not found in the '{name}' or it's parent,"
        f" but is included in the '{DICTS}'"
    )

    def __init__(self, attribute: str, name: str) -> None:
        super().__init__(self.message_template.format(attribute=attribute, name=name))


class MetaInheritDicts(type):
    def __new__(cls, name: str, bases: Tuple[type, ...], body: Dict[str, Any]):
        base = cast(Mapping[str, Any], bases[0].__dict__ if bases else {})
        attributes = body[DICTS] = body.get(DICTS, base.get(DICTS, set()))

        for attribute in attributes:
            base_value = base.get(attribute, None)
            value = body.get(attribute, None)

            if base_value is None and value is None:
                raise DictNotFoundError(attribute, name)
            body[attribute] = {**(base_value or {}), **(value or {})}

        return super().__new__(cls, name, bases, body)


class InheritDicts(metaclass=MetaInheritDicts):
    _dicts_to_inherit: Set[str] = set()
