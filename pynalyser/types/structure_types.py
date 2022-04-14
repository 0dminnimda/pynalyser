from typing import Dict, Union

import attr

from .base_types import SIGNATURE, AnyType, PynalyserType, SingleType


NotImplementedType = type(NotImplemented)
ReturnT = Union[PynalyserType, NotImplementedType]  # type: ignore


@attr.s(auto_attribs=True, hash=True)
class IntType(SingleType):
    name: str = "int"
    is_builtin: bool = True
    is_completed: bool = True

    @staticmethod
    def _sig():
        return (IntType(),)

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

    _sig_lt: SIGNATURE = _sig
    _sig_gt: SIGNATURE = _sig
    _sig_le: SIGNATURE = _sig
    _sig_ge: SIGNATURE = _sig
    _sig_eq: SIGNATURE = _sig
    _sig_ne: SIGNATURE = _sig

    def __add__(self, other: PynalyserType) -> ReturnT:
        if isinstance(other, IntType):
            return IntType()
        return NotImplemented
    _sig_add: SIGNATURE = lambda: (IntType(),)


@attr.s(auto_attribs=True, hash=True)
class BoolType(IntType):
    name: str = "bool"
    is_builtin: bool = True
    is_completed: bool = True


@attr.s(auto_attribs=True, hash=True)
class FloatType(SingleType):
    name: str = "float"
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

    # see docs.python.org/3/c-api/typeobj.html
    def __mul__(self, other: PynalyserType) -> ReturnT:
        if isinstance(other, IntType):
            return self
        return NotImplemented
    _sig_mul: SIGNATURE = lambda: (IntType(),)

    __rmul__ = __mul__
    _sig_rmul: SIGNATURE = lambda: (IntType(),)

    def __getitem__(self, item: PynalyserType) -> PynalyserType:
        return AnyType
    _sig_getitem: SIGNATURE = lambda: (AnyType,)


@attr.s(auto_attribs=True, hash=True)
class ListType(SequenceType):
    name: str = "list"
    is_builtin: bool = True
    is_completed: bool = True

    def __getitem__(self, item: PynalyserType) -> PynalyserType:
        if isinstance(item, IntType):
            return self.item_type
        if isinstance(item, SliceType):
            return self
        return NotImplemented
    _sig_getitem: SIGNATURE = lambda: (IntType(), SliceType())


@attr.s(auto_attribs=True, hash=True)
class TupleType(SequenceType):
    name: str = "tuple"
    is_builtin: bool = True
    is_completed: bool = True


@attr.s(auto_attribs=True, hash=True)
class SliceType(SingleType):
    name: str = "slice"
    is_builtin: bool = True
    is_completed: bool = True
