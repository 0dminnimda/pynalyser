import attr

from .base_types import AnyType, PynalyserType, DataType
from .op import REVERSED, Op, Signature, set_default_ops, set_op
from .inheritance import set_bases

# TODO: make a base class with __X__ and _sig_X annotated and defaulted
# the default value must be equal to a field not defined in the simulated class
# INFO: docs.python.org/3/reference/datamodel.html#object.__lt__
# INFO: docs.python.org/3/reference/datamodel.html#emulating-numeric-types


signature: Signature


NotImplementedType = DataType(name="NotImplementedType", is_builtin=True)


@attr.s(auto_attribs=True, hash=True, cmp=False)
class IntType(DataType):
    name: str = "int"
    is_builtin: bool = True
    is_completed: bool = True


set_bases(IntType, ())


signature = (IntType(),)


# also see "long_compare" in cpython github
@Op.sign(signature)
def _int_cmp(this: DataType, value: PynalyserType) -> DataType:
    if isinstance(value, IntType):
        return BoolType()
    return NotImplementedType


@Op.sign(signature)
def _int_binop(this: DataType, value: PynalyserType) -> DataType:
    if isinstance(value, IntType):
        return IntType()
    return NotImplementedType


@Op.sign(signature)
def _int__truediv__(this: DataType, value: PynalyserType) -> DataType:
    if isinstance(value, IntType):
        return FloatType()
    return NotImplementedType


# def __pow__(
#     self, value: PynalyserType, mod: Optional[PynalyserType] = None
# ) -> DataType:
#     if isinstance(value, IntType):
#         if isinstance(mod, IntType) or mod is None:
#             # FIXME: this is true only if 'value' is negative
#             # otherwise it's int
#             return FloatType()
#     return NotImplementedType


IntType.ops = IntType.ops.copy()
set_default_ops(IntType, _int_cmp)
set_default_ops(IntType, _int_binop, exclude={"__matmul__"})
set_op(IntType, _int__truediv__, "__truediv__")


@attr.s(auto_attribs=True, hash=True, cmp=False)
class BoolType(IntType):
    name: str = "bool"
    is_builtin: bool = True
    is_completed: bool = True


set_bases(BoolType, (IntType,))


@attr.s(auto_attribs=True, hash=True, cmp=False)
class FloatType(DataType):
    name: str = "float"
    is_builtin: bool = True
    is_completed: bool = True


set_bases(FloatType, ())


signature = (IntType(), FloatType())


@Op.sign(signature)
def _float_binop(this: DataType, value: PynalyserType) -> DataType:
    if isinstance(value, (IntType, FloatType)):
        return FloatType()
    return NotImplementedType


FloatType.ops = FloatType.ops.copy()
set_default_ops(FloatType, _float_binop, exclude={"__pow__", "__matmul__"})
set_default_ops(FloatType, _float_binop, REVERSED, exclude={"__rpow__", "__rmatmul__"})


@attr.s(auto_attribs=True, hash=True, cmp=False)
class SliceType(DataType):
    name: str = "slice"
    is_builtin: bool = True
    is_completed: bool = True


set_bases(SliceType, ())


@attr.s(auto_attribs=True, hash=True, cmp=False)
class IterableType(DataType):
    item_type: PynalyserType
    name: str = "Iterable"

    @property
    def as_str(self) -> str:
        return f"{super().as_str}[{self.item_type.as_str}]"


set_bases(IterableType, ())


@attr.s(auto_attribs=True, hash=True, cmp=False)  # auto_detect=True)
class SequenceType(IterableType):
    pass


set_bases(SequenceType, (IterableType,))


# TODO: not finished, see docs.python.org/3/library/collections.abc.html
# see docs.python.org/3/c-api/typeobj.html


@Op.sign((IntType(),))
def _seq__mul__(this: DataType, value: PynalyserType) -> DataType:
    if isinstance(value, IntType):
        return this
    return NotImplementedType


@Op.sign((AnyType,))
def _seq__getitem__(this: PynalyserType, item: PynalyserType) -> DataType:
    return AnyType


SequenceType.ops = SequenceType.ops.copy()
set_op(SequenceType, _seq__mul__, "__mul__")
set_op(SequenceType, _seq__mul__, "__rmul__")
set_op(SequenceType, _seq__getitem__, "__getitem__")


@attr.s(auto_attribs=True, hash=True, cmp=False)
class ListType(SequenceType):
    name: str = "list"
    is_builtin: bool = True
    is_completed: bool = True


set_bases(ListType, (SequenceType,))


@Op.sign((IntType(), SliceType()))
def _list__getitem__(this: ListType, item: PynalyserType) -> DataType:
    if isinstance(item, IntType):
        return this.item_type.deref(report=True)
    if isinstance(item, SliceType):
        return this
    return NotImplementedType


ListType.ops = ListType.ops.copy()
set_op(ListType, _list__getitem__, "__getitem__")


@attr.s(auto_attribs=True, hash=True, cmp=False)
class TupleType(SequenceType):
    name: str = "tuple"
    is_builtin: bool = True
    is_completed: bool = True


set_bases(TupleType, (SequenceType,))


del signature
