from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Type

import attr


# @attr.s(auto_attribs=True)
class PynalyserType:
    @property
    def as_str(self) -> str:
        raise NotImplementedError

    def deref(self) -> "PynalyserType":
        return self


@attr.s(auto_attribs=True, hash=True)
class UnionType(PynalyserType):
    types: Tuple[PynalyserType, ...] = attr.ib()

    @types.validator  # type: ignore
    def check(self, attribute: Any, value: Tuple[PynalyserType, ...]):
        if len(value) <= 1:
            raise ValueError("there should be more than 2 different types")

    @property
    def as_str(self) -> str:
        return f"Union[{', '.join(tp.as_str for tp in self.types)}]"

    # def __str__(self) -> str:
    #     return f"Union[{', '.join(str(tp) for tp in self.types)}]"

    @classmethod
    def make(cls, *types: PynalyserType,
             fallback: Optional[PynalyserType] = None) -> PynalyserType:
        new_types: List[PynalyserType] = []

        for tp in types:
            if isinstance(tp, cls):
                new_types.extend(tp.types)
            else:
                new_types.append(tp)

        unique_types = tuple(set(new_types))
        if len(unique_types) == 0:
            if fallback is not None:
                return fallback
            raise ValueError("length of types should not be 0")
        elif len(unique_types) == 1:
            return types[0]
        else:
            return cls(tuple(sorted(unique_types, key=lambda x: str(x))))


@attr.s(auto_attribs=True, hash=True)
class SingleType(PynalyserType):
    name: str = attr.ib(kw_only=True)
    is_builtin: bool = attr.ib(kw_only=True)

    dunder_signatures: Dict[str, DUNDER_SIGNATURE] = attr.ib(
        factory=dict, init=False, hash=False)

    is_completed: bool = attr.ib(default=False, kw_only=True)

    @property
    def as_str(self) -> str:
        return self.name


DUNDER_SIGNATURE = Tuple[Type[SingleType], ...]


AnyType = SingleType(name="object", is_builtin=False)
UnknownType = SingleType(name="object", is_builtin=False)
