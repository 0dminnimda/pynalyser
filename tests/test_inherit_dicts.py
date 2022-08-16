import pytest
from pynalyser.inherit_dicts import (
    DICTS,
    DictNotFoundError,
    InheritDicts,
    MetaInheritDicts,
)

from utils import do_test


def all_attrs(obj):
    return {name: getattr(obj, name) for name in dir(obj) if not name.startswith("__")}


def test_empty():
    class Cls1(metaclass=MetaInheritDicts):
        pass

    assert all_attrs(Cls1()) == {DICTS: set()}

    class Cls2(metaclass=MetaInheritDicts):
        _dicts_to_inherit = set()

    assert all_attrs(Cls2()) == {DICTS: set()}

    class Cls3(InheritDicts):
        pass

    assert all_attrs(Cls3()) == {DICTS: set()}

    class Cls4(InheritDicts):
        _dicts_to_inherit = set()

    assert all_attrs(Cls4()) == {DICTS: set()}


def test_one_dict():
    class Parent(InheritDicts):
        _dicts_to_inherit = {"a"}
        a = {1: 2}

    assert all_attrs(Parent()) == {DICTS: {"a"}, "a": {1: 2}}

    class Child(Parent):
        a = {3: 4}

    assert all_attrs(Child()) == {DICTS: {"a"}, "a": {1: 2, 3: 4}}

    class Child2(Child):
        a = {1: 5}

    assert all_attrs(Child2()) == {DICTS: {"a"}, "a": {1: 5, 3: 4}}


def test_two_dicts():
    class Parent(InheritDicts):
        _dicts_to_inherit = {"a", "b"}
        a = {1: 2}
        b = {10: 11}

    assert all_attrs(Parent()) == {DICTS: {"a", "b"}, "a": {1: 2}, "b": {10: 11}}

    class Child(Parent):
        b = {12: 13}

    assert all_attrs(Child()) == {DICTS: {"a", "b"}, "a": {1: 2}, "b": {10: 11, 12: 13}}

    class Child2(Child):
        a = {1: 5}

    assert all_attrs(Child2()) == {
        DICTS: {"a", "b"},
        "a": {1: 5},
        "b": {10: 11, 12: 13},
    }

    class Child3(Child2):
        a = {3: 4}
        b = {12: 0}

    assert all_attrs(Child3()) == {
        DICTS: {"a", "b"},
        "a": {1: 5, 3: 4},
        "b": {10: 11, 12: 0},
    }


def test_removal():
    class Parent(InheritDicts):
        _dicts_to_inherit = {"a"}
        a = {1: 2}

    assert all_attrs(Parent()) == {DICTS: {"a"}, "a": {1: 2}}

    class Child(Parent):
        _dicts_to_inherit = set()
        a = {3: 4}

    assert all_attrs(Child()) == {DICTS: set(), "a": {3: 4}}

    class Child2(Parent):
        _dicts_to_inherit = set()

    # regular inheritance
    assert all_attrs(Child2()) == {DICTS: set(), "a": {1: 2}}


def test_persists():
    class Parent(InheritDicts):
        _dicts_to_inherit = {"a"}
        a = {1: 2}

    assert all_attrs(Parent()) == {DICTS: {"a"}, "a": {1: 2}}

    class Child(Parent):
        pass

    assert all_attrs(Child()) == {DICTS: {"a"}, "a": {1: 2}}


def test_nonexisting():
    with pytest.raises(DictNotFoundError, match=str(DictNotFoundError("a", "Cls1"))):

        class Cls1(InheritDicts):
            _dicts_to_inherit = {"a"}

    with pytest.raises(DictNotFoundError, match=str(DictNotFoundError("b", "Cls2"))):

        class Cls2(InheritDicts):
            _dicts_to_inherit = {"a", "b"}
            a = {1: 2}


def test_as_a_whole():
    class A(InheritDicts):
        _dicts_to_inherit = {"a"}
        a = {1: 2}

    class B(A):
        a = {5: 6}

    class C(B):
        _dicts_to_inherit = {"a", "b"}
        a = {1: 8}
        b = {1: 9}

    class D(C):
        _dicts_to_inherit = {"b"}
        b = {2: 19}

    classes = [InheritDicts, A, B, C, D]
    values = [
        {DICTS: set()},
        {DICTS: {"a"}, "a": {1: 2}},
        {DICTS: {"a"}, "a": {1: 2, 5: 6}},
        {DICTS: {"b", "a"}, "a": {1: 8, 5: 6}, "b": {1: 9}},
        {DICTS: {"b"}, "a": {1: 8, 5: 6}, "b": {1: 9, 2: 19}},
    ]

    assert len(classes) == len(values)
    for cls, value in zip(classes, values):
        assert value == all_attrs(cls()), cls.__name__


if __name__ == "__main__":
    do_test(__file__)
