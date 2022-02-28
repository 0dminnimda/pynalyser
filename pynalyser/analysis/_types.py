from typing import Dict, List, Optional, Tuple, Type, TypeVar, Union

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
    @types.validator
    def check(self, attribute: attr.ib, value: Tuple[PynalyserType, ...]):
        if len(value) <= 1:
            raise ValueError("there should be more than 2 different types")

    @property
    def as_str(self) -> str:
        return f"Union[{', '.join(tp.as_str for tp in self.types)}]"

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
            return cls(unique_types)


DUNDER_SIGNATURE = Tuple[Type["SingleType"], ...]


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


AnyType = SingleType(name="object", is_builtin=False)
UnknownType = SingleType(name="object", is_builtin=False)


# T = TypeVar("T")

NotImplementedType = type(NotImplemented)
ReturnT = Union[PynalyserType, NotImplementedType]


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
    def _cmp(self, other) -> ReturnT:
        if isinstance(other, IntType):
            return BoolType()
        return NotImplemented

    __lt__ = _cmp
    __gt__ = _cmp
    __le__ = _cmp
    __ge__ = _cmp
    __eq__ = _cmp
    __ne__ = _cmp

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
