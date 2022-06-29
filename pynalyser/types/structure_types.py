from typing import Dict, Optional, Union

import attr

from .base_types import SIGNATURE, AnyType, PynalyserType, SingleType


NotImplementedType = type(NotImplemented)
ReturnT = Union[PynalyserType, NotImplementedType]  # type: ignore


# TODO: make a base class with __X__ and _sig_X annotated and defaulted
# the default value must be equal to a field not defined in the simulated class
# INFO: docs.python.org/3/reference/datamodel.html#object.__lt__
# INFO: docs.python.org/3/reference/datamodel.html#emulating-numeric-types

@attr.s(auto_attribs=True, hash=True, cmp=False)
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

    def _binop(self, other: PynalyserType) -> ReturnT:
        if isinstance(other, IntType):
            return IntType()
        return NotImplemented

    __add__ = _binop
    __sub__ = _binop
    __mul__ = _binop
    __mod__ = _binop
    __lshift__ = _binop
    __rshift__ = _binop
    __or__ = _binop
    __xor__ = _binop
    __and__ = _binop
    __floordiv__ = _binop

    def __truediv__(self, other: PynalyserType) -> ReturnT:
        if isinstance(other, IntType):
            return FloatType()
        return NotImplemented

    def __pow__(self, value: PynalyserType,
                mod: Optional[PynalyserType] = None) -> ReturnT:
        if isinstance(value, IntType):
            if isinstance(mod, IntType) or mod is None:
                # FIXME: this is true only if 'value' is negative
                # otherwise it's int
                return FloatType()
        return NotImplemented

    _sig_add: SIGNATURE = _sig
    _sig_sub: SIGNATURE = _sig
    _sig_mul: SIGNATURE = _sig
    _sig_truediv: SIGNATURE = _sig
    _sig_mod: SIGNATURE = _sig
    _sig_lshift: SIGNATURE = _sig
    _sig_rshift: SIGNATURE = _sig
    _sig_or: SIGNATURE = _sig
    _sig_xor: SIGNATURE = _sig
    _sig_and: SIGNATURE = _sig
    _sig_floordiv: SIGNATURE = _sig
    _sig_pow: SIGNATURE = _sig


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

    @staticmethod
    def _sig():
        return (IntType(), FloatType())

    def _binop(self, other: PynalyserType) -> ReturnT:
        if isinstance(other, (IntType, FloatType)):
            return FloatType()
        return NotImplemented

    __add__ = _binop
    __sub__ = _binop
    __mul__ = _binop
    __truediv__ = _binop
    __mod__ = _binop
    __lshift__ = _binop
    __rshift__ = _binop
    __or__ = _binop
    __xor__ = _binop
    __and__ = _binop
    __floordiv__ = _binop
    # __pow__ = _binop
    __radd__ = _binop
    __rsub__ = _binop
    __rmul__ = _binop
    __rtruediv__ = _binop
    __rmod__ = _binop
    __rlshift__ = _binop
    __rrshift__ = _binop
    __ror__ = _binop
    __rxor__ = _binop
    __rand__ = _binop
    __rfloordiv__ = _binop
    # __rpow__ = _binop

    _sig_add: SIGNATURE = _sig
    _sig_sub: SIGNATURE = _sig
    _sig_mul: SIGNATURE = _sig
    _sig_truediv: SIGNATURE = _sig
    _sig_mod: SIGNATURE = _sig
    _sig_lshift: SIGNATURE = _sig
    _sig_rshift: SIGNATURE = _sig
    _sig_or: SIGNATURE = _sig
    _sig_xor: SIGNATURE = _sig
    _sig_and: SIGNATURE = _sig
    _sig_floordiv: SIGNATURE = _sig
    # _sig_pow: SIGNATURE = _sig
    _sig_radd: SIGNATURE = _sig
    _sig_rsub: SIGNATURE = _sig
    _sig_rmul: SIGNATURE = _sig
    _sig_rtruediv: SIGNATURE = _sig
    _sig_rmod: SIGNATURE = _sig
    _sig_rlshift: SIGNATURE = _sig
    _sig_rrshift: SIGNATURE = _sig
    _sig_ror: SIGNATURE = _sig
    _sig_rxor: SIGNATURE = _sig
    _sig_rand: SIGNATURE = _sig
    _sig_rfloordiv: SIGNATURE = _sig
    # _sig_rpow: SIGNATURE = _sig


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
