from typing import Tuple, Type
from pynalyser.types.inheritance import Inheritable, is_subclass, is_type, set_bases
from pynalyser.types.exceptions import duplicate_base, invalid_mro
from utils import do_test, raises_instance


def make_class(
    name: str = "", bases: Tuple[Type[Inheritable], ...] = ()
) -> Type[Inheritable]:
    cls = type(name, (Inheritable,), {})
    set_bases(cls, bases)
    return cls


# some tests are adopted from cpython/Lib/test/test_descr.py
def test_no_inheritance():
    A = make_class("A")
    assert A.mro == (A,)


def test_single_inheritance():
    A = make_class("A")
    B = make_class("B", (A,))
    assert B.mro == (B, A)


def test_multiple_inheritance():
    A = make_class("A")
    A = make_class("A")
    B = make_class("B")
    C = make_class("C", (A, B))
    assert C.mro == (C, A, B)


def test_diamond_inheritance():
    A = make_class("A")
    B = make_class("B", (A,))
    C = make_class("C", (A,))
    D = make_class("D", (B, C))
    assert D.mro == (D, B, C, A)

    E = make_class("E", (C, B))
    assert E.mro == (E, C, B, A)

    with raises_instance(invalid_mro(["D", "E"])):
        make_class("F", (D, E))

    with raises_instance(invalid_mro(["E", "D"])):
        make_class("G", (E, D))


def test_ex5_from_c3_switch():
    A = make_class("A")
    B = make_class("B")
    C = make_class("C")
    X = make_class("X", (A,))
    Y = make_class("Y", (A,))
    Z = make_class("Z", (X, B, Y, C))
    assert Z.mro == (Z, X, B, Y, A, C)


def test_monotonicity():
    Boat = make_class("Boat")
    DayBoat = make_class("DayBoat", (Boat,))
    WheelBoat = make_class("WheelBoat", (Boat,))
    EngineLess = make_class("EngineLess", (DayBoat,))
    SmallMultihull = make_class("SmallMultihull", (DayBoat,))
    PedalWheelBoat = make_class("PedalWheelBoat", (EngineLess, WheelBoat))
    SmallCatamaran = make_class("SmallCatamaran", (SmallMultihull,))
    Pedalo = make_class("Pedalo", (PedalWheelBoat, SmallCatamaran))
    assert PedalWheelBoat.mro == (
        PedalWheelBoat,
        EngineLess,
        DayBoat,
        WheelBoat,
        Boat,
    )
    assert SmallCatamaran.mro == (SmallCatamaran, SmallMultihull, DayBoat, Boat)
    assert Pedalo.mro == (
        Pedalo,
        PedalWheelBoat,
        EngineLess,
        SmallCatamaran,
        SmallMultihull,
        DayBoat,
        WheelBoat,
        Boat,
    )


def test_consistency_with_epg():
    Pane = make_class("Pane")
    ScrollingMixin = make_class("ScrollingMixin")
    EditingMixin = make_class("EditingMixin")
    ScrollablePane = make_class("ScrollablePane", (Pane, ScrollingMixin))
    EditablePane = make_class("EditablePane", (Pane, EditingMixin))
    EditableScrollablePane = make_class(
        "EditableScrollablePane", (ScrollablePane, EditablePane)
    )
    assert EditableScrollablePane.mro == (
        EditableScrollablePane,
        ScrollablePane,
        EditablePane,
        Pane,
        ScrollingMixin,
        EditingMixin,
    )


def test_mro_disagreement():
    # FIXME: the exact msg is generally considered an impl detail
    # if util.check_impl_detail(): check message

    A = make_class("A")
    B = make_class("B", (A,))
    C = make_class("C")

    with raises_instance(duplicate_base("A")):
        make_class("X", (A, A))

    with raises_instance(invalid_mro(["A", "B"])):
        make_class("X", (A, B))

    with raises_instance(invalid_mro(["A", "C", "B"])):
        make_class("X", (A, C, B))

    GridLayout = make_class("GridLayout")
    HorizontalGrid = make_class("HorizontalGrid", (GridLayout,))
    VerticalGrid = make_class("VerticalGrid", (GridLayout,))
    HVGrid = make_class("HVGrid", (HorizontalGrid, VerticalGrid))
    VHGrid = make_class("VHGrid", (VerticalGrid, HorizontalGrid))

    with raises_instance(invalid_mro(["HVGrid", "VHGrid"])):
        make_class("ConfusedGrid", (HVGrid, VHGrid))


# TODO: add cpython/Lib/test/test_genericclass.py


def test_is_type():
    A = make_class("A")
    B = make_class("B")
    assert not is_type(A, B)
    assert not is_type(A, B())
    assert not is_type(A(), B)
    assert not is_type(A(), B())

    C = make_class("C")
    assert is_type(C, C)
    assert is_type(C, C())
    assert is_type(C(), C)
    assert is_type(C(), C())


def test_is_subclass():
    A = make_class("A")
    B = make_class("B")

    assert not is_subclass(A,   B)
    assert not is_subclass(A,   B())
    assert not is_subclass(A(), B)
    assert not is_subclass(A(), B())

    assert not is_subclass(B,   A)
    assert not is_subclass(B,   A())
    assert not is_subclass(B(), A)
    assert not is_subclass(B(), A())

    C = make_class("C")
    D = make_class("D", (C,))

    assert is_subclass(D,   C)
    assert is_subclass(D,   C())
    assert is_subclass(D(), C)
    assert is_subclass(D(), C())

    assert not is_subclass(C,   D)
    assert not is_subclass(C,   D())
    assert not is_subclass(C(), D)
    assert not is_subclass(C(), D())

    E = make_class("E", (D, A))

    assert is_subclass(E,   D)
    assert is_subclass(E,   D())
    assert is_subclass(E(), D)
    assert is_subclass(E(), D())

    assert is_subclass(E,   C)
    assert is_subclass(E,   C())
    assert is_subclass(E(), C)
    assert is_subclass(E(), C())

    assert is_subclass(E,   A)
    assert is_subclass(E,   A())
    assert is_subclass(E(), A)
    assert is_subclass(E(), A())


def test_is_subclass_tuple():
    A = make_class("A")

    assert not is_subclass(A, ())
    assert not is_subclass(A(), ())

    B = make_class("B")
    C = make_class("C")

    assert not is_subclass(A, (B, C))
    assert not is_subclass(A, (B, C()))
    assert not is_subclass(A, (B(), C))
    assert not is_subclass(A, (B(), C()))

    assert not is_subclass(A(), (B, C))
    assert not is_subclass(A(), (B, C()))
    assert not is_subclass(A(), (B(), C))
    assert not is_subclass(A(), (B(), C()))

    D = make_class("D", (A,))

    assert is_subclass(D, (B, A))
    assert is_subclass(D, (B, A()))
    assert is_subclass(D, (B(), A))
    assert is_subclass(D, (B(), A()))

    assert is_subclass(D(), (B, A))
    assert is_subclass(D(), (B, A()))
    assert is_subclass(D(), (B(), A))
    assert is_subclass(D(), (B(), A()))


if __name__ == "__main__":
    do_test(__file__)
