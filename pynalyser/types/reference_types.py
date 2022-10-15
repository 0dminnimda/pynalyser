from typing import TYPE_CHECKING, List, Optional, Tuple

import attr

from .. import reports
from .base_types import AnyType, PynalyserType, SingleType, UnionType, UnknownType
from .exceptions import (
    binary_not_supported,
    compare_not_supported,
    not_iterable,
    not_subscriptable,
)
from .op import Op, Signature
from .structure_types import BoolType, IntType, IterableType, NotImplementedType

if TYPE_CHECKING:
    from ..symbol import Symbol


Calls = List[Tuple[Optional[Op], bool]]


@attr.s(auto_attribs=True, auto_detect=True)
class SymbolType(PynalyserType):
    name: str
    symbol: "Symbol"

    def deref(self, report: bool) -> SingleType:
        return self.symbol.type.deref(report)

    def __hash__(self) -> int:
        return hash((type(self), self.name))


def infer_signature_type(type: SingleType, signature: Signature) -> SingleType:
    if type.issubclass(signature):
        return type
    if not type.is_completed:
        return UnionType(*signature).deref(report=False)
    return type


def narrow_type(
    calls: Calls, lhs: SingleType, rhs: SingleType
) -> Tuple[SingleType, SingleType]:

    for method, reflected in calls:
        if method is None:
            # TODO: we should add the respective dunder method to the type
            # method = Op.sign((lhs if reflected else rhs,))(lambda)
            continue
        else:
            signature = method.signature
            if reflected:
                lhs = infer_signature_type(lhs, signature)
            else:
                rhs = infer_signature_type(rhs, signature)

    return lhs, rhs


@attr.s(auto_attribs=True, hash=True)
class BinOpType(PynalyserType):
    lhs: PynalyserType
    op: str
    rhs: PynalyserType

    @staticmethod
    def prepare_calls(lhs: SingleType, op: str, rhs: SingleType) -> Calls:
        forward = f"__{op}__"
        reflected = f"__r{op}__"

        lhs_op = lhs.ops.get(forward)
        rhs_op = rhs.ops.get(reflected)

        call_lhs = lhs_op, False
        call_rhs = rhs_op, True

        if lhs.is_type(rhs):
            return [call_lhs]
        # will "lhs.ops.get(reflected) is not rhs_op" be not triggered when needed?
        elif rhs.issubclass(lhs) and lhs.ops.get(reflected) is not rhs_op:
            return [call_rhs, call_lhs]
        else:
            return [call_lhs, call_rhs]

    @classmethod
    def do_binary_op(
        cls, lhs: SingleType, op: str, rhs: SingleType, report: bool = True
    ) -> SingleType:
        for method, reflected in cls.prepare_calls(lhs, op, rhs):
            if method is None:
                continue

            if reflected:
                value = method(rhs, lhs)
            else:
                value = method(lhs, rhs)

            if value is not NotImplementedType:
                return value

        if report:
            reports.report(binary_not_supported(op, lhs.name, rhs.name))

        return AnyType

    def __attrs_post_init__(self) -> None:
        lhs = self.lhs.deref(report=False)
        rhs = self.rhs.deref(report=False)

        lhs, rhs = narrow_type(self.prepare_calls(lhs, self.op, rhs), lhs, rhs)

        if isinstance(self.lhs, SymbolType):
            self.lhs.symbol.type = lhs

        if isinstance(self.rhs, SymbolType):
            self.rhs.symbol.type = rhs

    def deref(self, report: bool) -> SingleType:
        return self.do_binary_op(
            self.lhs.deref(report), self.op, self.right.deref(report), report
        )


_CMP = ["gt", "ge", "eq", "ne", "lt", "le"]
SWAPPED_CMP = {v1: v2 for v1, v2 in zip(_CMP, _CMP[::-1])}


@attr.s(auto_attribs=True, hash=True)
class CompareOpType(PynalyserType):
    lhs: PynalyserType
    ops: List[str]
    comparators: List[PynalyserType]

    @staticmethod
    def prepare_calls(lhs: SingleType, op: str, rhs: SingleType) -> Calls:
        if op == "is":
            return []

        if op == "contains":
            return [(rhs.ops.get(op), True)]

        # richcompare
        f_lhs = lhs.ops.get(f"__{op}__")
        f_rhs = rhs.ops.get(f"__{SWAPPED_CMP[op]}__")

        call_lhs = f_lhs, False
        call_rhs = f_rhs, True

        if not lhs.is_type(rhs) and rhs.issubclass(lhs):
            return [call_rhs, call_lhs]
        else:
            return [call_lhs, call_rhs]

    @classmethod
    def do_is(
        cls, lhs: SingleType, op: str, rhs: SingleType, report: bool = True
    ) -> SingleType:

        calls = cls.prepare_calls(lhs, op, rhs)
        assert len(calls) == 0, f"calls were prepared for '{op}' operation"

        # lhs.id == rhs.id or something, idk
        return BoolType()

    @classmethod
    def do_contains(
        cls, lhs: SingleType, op: str, rhs: SingleType, report: bool = True
    ) -> SingleType:

        for method, reflected in cls.prepare_calls(lhs, op, rhs):
            assert reflected, f"'{op}' operation is not reflected"

            if method is None:
                continue

            return method(rhs, lhs)

        # TODO: _PySequence_IterSearch(rhs, lhs, PY_ITERSEARCH_CONTAINS)

        if report:
            reports.report(not_iterable(rhs.name))

        return AnyType

    @classmethod
    def do_richcompare(
        cls, lhs: SingleType, op: str, rhs: SingleType, report: bool = True
    ) -> SingleType:

        for method, reflected in cls.prepare_calls(lhs, op, rhs):
            if method is None:
                continue

            if reflected:
                value = method(rhs, lhs)
            else:
                value = method(lhs, rhs)

            if value is not NotImplementedType:
                return value

        # if neither object implements it,
        # provide a sensible default for == and !=
        if op == "eq":
            return cls.do_is(lhs, op, rhs)
        if op == "ne":
            # TODO: use UnaryOpType.do_not (it's special,
            # so no problems with excessive calls to dunder/other methods)
            return cls.do_is(lhs, op, rhs)

        if report:
            reports.report(compare_not_supported(op, lhs.name, rhs.name))

        return AnyType

    @staticmethod
    def process_op(op: str) -> Tuple[str, bool]:
        op, _, neg = op.partition("_")
        return op, neg == "not"

    @classmethod
    def do_compare_op(
        cls, lhs: SingleType, op: str, rhs: SingleType, report: bool = True
    ) -> SingleType:

        # TODO: the same deal - use UnaryOpType.do_not for negate
        op, negate = cls.process_op(op)

        if op == "is":
            return cls.do_is(lhs, op, rhs, report)

        if op == "contains":
            return cls.do_contains(lhs, op, rhs, report)

        return cls.do_richcompare(lhs, op, rhs, report)

    def deref_comparators(self, report: bool) -> List[SingleType]:
        return [
            comparator.deref(report) for comparator in [self.lhs] + self.comparators
        ]

    def __attrs_post_init__(self) -> None:
        # comparators = self.deref_comparators(report=False)
        # for lhs, op, rhs in zip(comparators, self.ops, comparators[1:]):
        #     op = self.process_op(op)[0]
        #     lhs, rhs = narrow_type(self.prepare_calls(lhs, op, rhs), lhs, rhs)

        lhs = self.lhs.deref(report=False)
        rhs = self.comparators[0].deref(report=False)

        op = self.process_op(self.ops[0])[0]
        lhs, rhs = narrow_type(self.prepare_calls(lhs, op, rhs), lhs, rhs)

        if isinstance(self.lhs, SymbolType):
            self.lhs.symbol.type = lhs

        if isinstance(self.comparators[0], SymbolType):
            self.comparators[0].symbol.type = rhs

    def deref(self, report: bool) -> SingleType:
        comparators = self.deref_comparators(report)

        # TODO: implement and use all()
        for lhs, op, rhs in zip(comparators, self.ops, comparators[1:]):
            self.do_compare_op(lhs, op, rhs, report)

        return BoolType()


@attr.s(auto_attribs=True, hash=True)
class SubscriptType(PynalyserType):
    value: PynalyserType
    slice: PynalyserType

    def deref(self, report: bool) -> SingleType:
        value = self.value.deref(report)
        method = value.ops.get("__getitem__")

        if method is not None:
            return method(value, self.slice.deref(report))

        if report:
            reports.report(not_subscriptable(value.name))

        return AnyType


@attr.s(auto_attribs=True, hash=True)
class ItemType(PynalyserType):
    iterable: PynalyserType

    def __attrs_post_init__(self) -> None:
        tp = self.iterable.deref(report=False)
        if tp is UnknownType:
            if isinstance(self.iterable, SymbolType):
                self.iterable.symbol.type = IterableType(
                    item_type=UnknownType, is_builtin=False
                )
            # XXX: should we let it be and cause an error?
            # else:
            #     self.iterable = IterableType(
            #         item_type=UnknownType, is_builtin=False)

    def deref(self, report: bool) -> SingleType:
        return self.iterable.deref(report).item_type.deref(report)  # type: ignore


@attr.s(auto_attribs=True, hash=True)
class CallType(PynalyserType):
    func: PynalyserType
    args: Tuple[PynalyserType, ...]
    keywords: Tuple[Tuple[Optional[str], PynalyserType], ...]

    def deref(self, report: bool) -> SingleType:
        if isinstance(self.func, SymbolType) and self.func.name == "range":
            return IterableType(
                item_type=IntType(), is_builtin=False
            )  # XXX: is_builtin??

        return AnyType
