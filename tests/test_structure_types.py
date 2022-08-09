from pynalyser.types import *
from pynalyser.analysers.type_inference import CMPOP, BINOP

from utils import do_test

import operator

# you cannot overwrite 'is' and True/False != BoolType :(
# operator.__is__ = operator.is_  # type: ignore[attr-defined]
# operator.__is_not__ = operator.is_not  # type: ignore[attr-defined]
operator.__contains_not__ = lambda a, b: a not in b  # type: ignore[attr-defined]


def check_binop(op, lhs, rhs, result):
    assert isinstance(getattr(operator, f"__{op}__")(lhs, rhs), result)
    assert isinstance(BinOpType(lhs, op, rhs).deref(report=True), result)


def check_cmpop(op, lhs, rhs, result):
    if op not in ("is", "is_not"):
        assert isinstance(getattr(operator, f"__{op}__")(lhs, rhs), result)
    assert isinstance(CompareOpType(lhs, [op], [rhs]).deref(report=True), result)


BINOPS = set(BINOP.values())

CMPOPS = set(CMPOP.values())


def test_int_binop():
    for op in BINOPS - {"matmul", "truediv", "pow"}:
        check_binop(op, IntType(), IntType(), IntType)
    check_binop("truediv", IntType(), IntType(), FloatType)
    # IntType() ** X() can be different, depending on the sign


def test_int_cmp():
    for op in CMPOPS - {"contains", "contains_not"}:
        check_cmpop(op, IntType(), IntType(), BoolType)


def test_float_binop():
    for op in BINOPS - {"matmul", "pow"}:
        check_binop(op, FloatType(), IntType(), FloatType)
        check_binop(op, IntType(), FloatType(), FloatType)
        check_binop(op, FloatType(), FloatType(), FloatType)
    # FloatType() ** X() can be different, depending on the sign


def test_sequence():
    seq = SequenceType(item_type=PynalyserType(), is_builtin=False)
    check_binop("mul", seq, IntType(), SequenceType)
    check_binop("mul", IntType(), seq, SequenceType)
    assert seq[SliceType()] is AnyType
    assert SubscriptType(seq, SliceType()).deref(True) is AnyType


def test_list():
    lst = ListType(
        item_type=SingleType(name="test", is_builtin=False), is_builtin=False
    )
    assert isinstance(lst * IntType(), SequenceType)
    assert lst[IntType()] is lst.item_type
    assert SubscriptType(lst, IntType()).deref(True) is lst.item_type
    assert isinstance(lst[SliceType()], ListType)
    assert isinstance(SubscriptType(lst, SliceType()).deref(True), ListType)


def test_tuple():
    tpl = TupleType(item_type=PynalyserType(), is_builtin=False)
    assert isinstance(tpl * IntType(), SequenceType)
    assert tpl[SliceType()] is AnyType
    assert SubscriptType(tpl, SliceType()).deref(True) is AnyType


if __name__ == "__main__":
    do_test(__file__)
