from typing import TYPE_CHECKING, Callable, Dict, NamedTuple, Optional, Set, Tuple, Type

if TYPE_CHECKING:
    from .base_types import PynalyserType, SingleType


OpFunction = Callable[..., "SingleType"]
Signature = Tuple["SingleType", ...]


class Op(NamedTuple):
    function: OpFunction
    signature: Signature = tuple()

    def __call__(
        self, *args: "PynalyserType", **kwargs: "PynalyserType"
    ) -> "SingleType":
        return self.function(*args, **kwargs)

    def __repr__(self) -> str:
        return f"Op({self.function.__name__}, {self.signature})"

    @classmethod
    def sign(cls, signature: Signature = tuple()):
        def wrapper(function: OpFunction):
            return cls(function, signature)

        return wrapper


DEFAULT_FUNCTIONS = {
    "cmp": {
        "__lt__",
        "__le__",
        "__eq__",
        "__ne__",
        "__gt__",
        "__ge__",
    },
    "binop": {
        "__add__",
        "__sub__",
        "__mul__",
        "__matmul__",
        "__truediv__",
        "__floordiv__",
        "__mod__",
        "__divmod__",
        "__pow__",
        "__lshift__",
        "__rshift__",
        "__and__",
        "__xor__",
        "__or__",
    },
    "rev_binop": {
        "__radd__",
        "__rsub__",
        "__rmul__",
        "__rmatmul__",
        "__rtruediv__",
        "__rfloordiv__",
        "__rmod__",
        "__rdivmod__",
        "__rpow__",
        "__rlshift__",
        "__rrshift__",
        "__rand__",
        "__rxor__",
        "__ror__",
    },
}


OpDict = Dict[str, Op]


class OpCarrier:
    ops: OpDict = {}

    def _get_op_func(self, name: str) -> OpFunction:
        try:
            return self.ops[name].function
        except KeyError:
            return self._default_op_func

    @staticmethod
    def _default_op_func(*args, **kwargs) -> "SingleType":
        from .structure_types import NotImplementedType

        return NotImplementedType


def set_op(cls: Type[OpCarrier], op: Op, name: Optional[str] = None) -> None:
    if name is None:
        name = op.function.__name__
    cls.ops[name] = op


NORMAL = False
REVERSED = True


def set_default_ops(
    cls: Type[OpCarrier],
    op: Op,
    reversed: bool = False,
    name: Optional[str] = None,
    *,
    exclude: Optional[Set[str]] = None,
) -> None:
    if name is None:
        name = op.function.__name__
    name = op.function.__name__.split("_")[-1]
    if reversed:
        name = "rev_" + name

    exclude = exclude or set()
    cls.ops.update(dict.fromkeys(DEFAULT_FUNCTIONS[name] - exclude, op))
