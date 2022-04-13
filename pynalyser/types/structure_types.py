from typing import Dict, Union

import attr

from .base_types import DUNDER_SIGNATURE, AnyType, PynalyserType, SingleType


NotImplementedType = type(NotImplemented)
ReturnT = Union[PynalyserType, NotImplementedType]  # type: ignore


@attr.s(auto_attribs=True, hash=True)
class IntType(SingleType):
    name: str = "int"
    is_builtin: bool = True

    dunder_signatures: Dict[str, DUNDER_SIGNATURE] = attr.ib(
        factory=lambda: {
            "lt": (IntType,),
            "gt": (IntType,),
            "le": (IntType,),
            "ge": (IntType,),
            "eq": (IntType,),
            "ne": (IntType,),
        },
        init=False, hash=False)

    is_completed: bool = True

    # also see "long_compare" in cpython github
    def _cmp(self, other: PynalyserType) -> ReturnT:
        if isinstance(other, IntType):
            return BoolType()
        return NotImplemented

    __lt__ = _cmp  # type: ignore
    __gt__ = _cmp  # type: ignore
    __le__ = _cmp  # type: ignore
    __ge__ = _cmp  # type: ignore
    __eq__ = _cmp  # type: ignore
    __ne__ = _cmp  # type: ignore

    # dunder_signatures["lt"] = [IntType]
    # dunder_signatures["gt"] = [IntType]
    # dunder_signatures["le"] = [IntType]
    # dunder_signatures["ge"] = [IntType]
    # dunder_signatures["eq"] = [IntType]
    # dunder_signatures["ne"] = [IntType]


@attr.s(auto_attribs=True, hash=True)
class BoolType(IntType):
    name: str = "bool"
    is_builtin: bool = True

    is_completed: bool = True


@attr.s(auto_attribs=True)
class IterableType(SingleType):
    item_type: PynalyserType
    name: str = "Iterable"

    @property
    def as_str(self) -> str:
        return f"{super().as_str}[{self.item_type.as_str}]"


@attr.s(auto_attribs=True, hash=True, auto_detect=True)
class SequenceType(IterableType):
    # TODO: not finshed, see docs.python.org/3/library/collections.abc.html

    dunder_signatures: Dict[str, DUNDER_SIGNATURE] = attr.ib(
        factory=lambda: {
            "mul":     (IntType,      ),
            "rmul":    (IntType,      ),
            "getitem": (type(AnyType),)
        },
        init=False, hash=False)

    # see docs.python.org/3/c-api/typeobj.html
    def __mul__(self, other: PynalyserType) -> ReturnT:
        if isinstance(other, IntType):
            return self
        return NotImplemented
    # dunder_signatures["mul"] = [IntType]

    __rmul__ = __mul__
    # dunder_signatures["rmul"] = [IntType]

    def __getitem__(self, item: PynalyserType) -> PynalyserType:
        return AnyType


@attr.s(auto_attribs=True, hash=True)
class SliceType(SingleType):
    name: str = "slice"
    is_builtin: bool = True

    is_completed: bool = True


@attr.s(auto_attribs=True, hash=True)
class ListType(SequenceType):
    name: str = "list"
    is_builtin: bool = True

    dunder_signatures: Dict[str, DUNDER_SIGNATURE] = attr.ib(
        factory=lambda: {
            "mul":     (IntType,           ),
            "rmul":    (IntType,           ),
            "getitem": (IntType, SliceType,),
        },
        init=False, hash=False)

    is_completed: bool = True

    def __getitem__(self, item: PynalyserType) -> PynalyserType:
        if isinstance(item, IntType):
            return self.item_type
        if isinstance(item, SliceType):
            return self
        return NotImplemented


@attr.s(auto_attribs=True, hash=True)
class TupleType(SequenceType):
    name: str = "tuple"
    is_builtin: bool = True

    is_completed: bool = True
