from pynalyser.types import *

from utils import do_test


def test_int_binop():
    assert isinstance(IntType() + IntType(), IntType)
    assert isinstance(IntType() - IntType(), IntType)
    assert isinstance(IntType() * IntType(), IntType)
    assert isinstance(IntType() / IntType(), FloatType)
    assert isinstance(IntType() % IntType(), IntType)
    assert isinstance(IntType() << IntType(), IntType)
    assert isinstance(IntType() >> IntType(), IntType)
    assert isinstance(IntType() | IntType(), IntType)
    assert isinstance(IntType() ^ IntType(), IntType)
    assert isinstance(IntType() & IntType(), IntType)
    assert isinstance(IntType() // IntType(), IntType)
    # IntType() ** X() can be different, depending on the sign


def test_int_cmp():
    assert isinstance(IntType() < IntType(), BoolType)
    assert isinstance(IntType() > IntType(), BoolType)
    assert isinstance(IntType() <= IntType(), BoolType)
    assert isinstance(IntType() >= IntType(), BoolType)
    assert isinstance(IntType() == IntType(), BoolType)
    assert isinstance(IntType() != IntType(), BoolType)


def test_float_binop():
    assert isinstance(FloatType() + IntType(), FloatType)
    assert isinstance(FloatType() - IntType(), FloatType)
    assert isinstance(FloatType() * IntType(), FloatType)
    assert isinstance(FloatType() / IntType(), FloatType)
    assert isinstance(FloatType() % IntType(), FloatType)
    assert isinstance(FloatType() << IntType(), FloatType)
    assert isinstance(FloatType() >> IntType(), FloatType)
    assert isinstance(FloatType() | IntType(), FloatType)
    assert isinstance(FloatType() ^ IntType(), FloatType)
    assert isinstance(FloatType() & IntType(), FloatType)
    assert isinstance(FloatType() // IntType(), FloatType)
    # FloatType() ** X() can be different, depending on the sign

    assert isinstance(FloatType() + FloatType(), FloatType)
    assert isinstance(FloatType() - FloatType(), FloatType)
    assert isinstance(FloatType() * FloatType(), FloatType)
    assert isinstance(FloatType() / FloatType(), FloatType)
    assert isinstance(FloatType() % FloatType(), FloatType)
    assert isinstance(FloatType() << FloatType(), FloatType)
    assert isinstance(FloatType() >> FloatType(), FloatType)
    assert isinstance(FloatType() | FloatType(), FloatType)
    assert isinstance(FloatType() ^ FloatType(), FloatType)
    assert isinstance(FloatType() & FloatType(), FloatType)
    assert isinstance(FloatType() // FloatType(), FloatType)
    # FloatType() ** X() can be different, depending on the sign


def test_sequence():
    seq = SequenceType(item_type=PynalyserType(), is_builtin=False)
    assert isinstance(seq * IntType(), SequenceType)
    assert seq[PynalyserType()] is AnyType


def test_list():
    lst = ListType(item_type=PynalyserType(), is_builtin=False)
    assert isinstance(lst * IntType(), SequenceType)
    assert lst[IntType()] is lst.item_type
    assert isinstance(lst[SliceType()], ListType)


def test_tuple():
    tpl = TupleType(item_type=PynalyserType(), is_builtin=False)
    assert isinstance(tpl * IntType(), SequenceType)
    assert tpl[PynalyserType()] is AnyType


if __name__ == "__main__":
    do_test(__file__)
