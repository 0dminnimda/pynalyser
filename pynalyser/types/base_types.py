from typing import Any, Callable, List, Optional, Tuple, Union
from typing_extensions import Literal

import attr

from .op import OpCarrier


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
    def make(
        cls, *types: PynalyserType, fallback: Optional[PynalyserType] = None
    ) -> PynalyserType:
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


NotImplementedLiteral = Literal[NotImplemented]  # type: ignore
Return = Union["SingleType", NotImplementedLiteral]


@attr.s(auto_attribs=True, hash=True, cmp=False)
class SingleType(PynalyserType, OpCarrier):
    name: str = attr.ib(kw_only=True)
    is_builtin: bool = attr.ib(kw_only=True)
    # XXX: why do we need is_completed?
    is_completed: bool = attr.ib(default=False, kw_only=True)

    @property
    def as_str(self) -> str:
        return self.name

    # Those methods are not participating in the actual analysis (OpCarrier.ops does)
    # Those are just for fancy user interface

    def _run_op(self, op: str, *args, **kwargs) -> Return:
        from .structure_types import NotImplementedType

        value = self._get_op_func(op)(*args, **kwargs)

        if value is NotImplementedType:
            return NotImplemented

        return value

    # Comparisons
    def __lt__(self, value: PynalyserType) -> Return:
        return self._run_op("__lt__", self, value)

    def __le__(self, value: PynalyserType) -> Return:
        return self._run_op("__le__", self, value)

    def __eq__(self, value: PynalyserType) -> Return:  # type: ignore[override]
        return self._run_op("__eq__", self, value)

    def __ne__(self, value: PynalyserType) -> Return:  # type: ignore[override]
        return self._run_op("__ne__", self, value)

    def __gt__(self, value: PynalyserType) -> Return:
        return self._run_op("__gt__", self, value)

    def __ge__(self, value: PynalyserType) -> Return:
        return self._run_op("__ge__", self, value)

    # Binary operation
    def __add__(self, value: PynalyserType) -> Return:
        return self._run_op("__add__", self, value)

    def __sub__(self, value: PynalyserType) -> Return:
        return self._run_op("__sub__", self, value)

    def __mul__(self, value: PynalyserType) -> Return:
        return self._run_op("__mul__", self, value)

    def __matmul__(self, value: PynalyserType) -> Return:
        return self._run_op("__matmul__", self, value)

    def __truediv__(self, value: PynalyserType) -> Return:
        return self._run_op("__truediv__", self, value)

    def __floordiv__(self, value: PynalyserType) -> Return:
        return self._run_op("__floordiv__", self, value)

    def __mod__(self, value: PynalyserType) -> Return:
        return self._run_op("__mod__", self, value)

    def __divmod__(self, value: PynalyserType) -> Return:
        return self._run_op("__divmod__", self, value)

    # XXX: 'Optional' is a hack, it probably should be handled differently
    def __pow__(
        self, value: PynalyserType, mod: Optional[PynalyserType] = None
    ) -> Return:
        if mod is None:
            return self._run_op("__pow__", self, value)
        return self._run_op("__pow__", self, value, mod)

    def __lshift__(self, value: PynalyserType) -> Return:
        return self._run_op("__lshift__", self, value)

    def __rshift__(self, value: PynalyserType) -> Return:
        return self._run_op("__rshift__", self, value)

    def __and__(self, value: PynalyserType) -> Return:
        return self._run_op("__and__", self, value)

    def __xor__(self, value: PynalyserType) -> Return:
        return self._run_op("__xor__", self, value)

    def __or__(self, value: PynalyserType) -> Return:
        return self._run_op("__or__", self, value)

    # Reversed binary operation
    def __radd__(self, value: PynalyserType) -> Return:
        return self._run_op("__radd__", self, value)

    def __rsub__(self, value: PynalyserType) -> Return:
        return self._run_op("__rsub__", self, value)

    def __rmul__(self, value: PynalyserType) -> Return:
        return self._run_op("__rmul__", self, value)

    def __rmatmul__(self, value: PynalyserType) -> Return:
        return self._run_op("__rmatmul__", self, value)

    def __rtruediv__(self, value: PynalyserType) -> Return:
        return self._run_op("__rtruediv__", self, value)

    def __rfloordiv__(self, value: PynalyserType) -> Return:
        return self._run_op("__rfloordiv__", self, value)

    def __rmod__(self, value: PynalyserType) -> Return:
        return self._run_op("__rmod__", self, value)

    def __rdivmod__(self, value: PynalyserType) -> Return:
        return self._run_op("__rdivmod__", self, value)

    # XXX: 'Optional' is a hack, it probably should be handled differently
    def __rpow__(
        self, value: PynalyserType, mod: Optional[PynalyserType] = None
    ) -> Return:
        if mod is None:
            return self._run_op("__rpow__", self, value)
        return self._run_op("__rpow__", self, value, mod)

    def __rlshift__(self, value: PynalyserType) -> Return:
        return self._run_op("__rlshift__", self, value)

    def __rrshift__(self, value: PynalyserType) -> Return:
        return self._run_op("__rrshift__", self, value)

    def __rand__(self, value: PynalyserType) -> Return:
        return self._run_op("__rand__", self, value)

    def __rxor__(self, value: PynalyserType) -> Return:
        return self._run_op("__rxor__", self, value)

    def __ror__(self, value: PynalyserType) -> Return:
        return self._run_op("__ror__", self, value)

    # Other magic
    def __getitem__(self, value: PynalyserType) -> Return:
        return self._run_op("__getitem__", self, value)


AnyType = SingleType(name="object", is_builtin=False)
UnknownType = SingleType(name="object", is_builtin=False)
# invariant, cool name huh ;)
