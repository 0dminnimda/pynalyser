from typing import List, Optional, Tuple

import attr

from ..symbol import Symbol
from .base_types import (AnyType, PynalyserType, SingleType, UnionType,
                         UnknownType)
from .structure_types import IntType, IterableType


@attr.s(auto_attribs=True, auto_detect=True)
class SymbolType(PynalyserType):
    name: str
    symbol: Symbol

    def deref(self) -> PynalyserType:
        return self.symbol.type.deref()

    def __hash__(self) -> int:
        return hash((type(self), self.name))


binop_s = {
    "Add": "+",
    "Sub": "-",
    "MatMult": "@",
    "Mult": "*",
    "Div": "/",
    "Mod": "%",
    "LShift": "<<",
    "RShift": ">>",
    "BitOr": "|",
    "BitXor": "^",
    "BitAnd": "&",
    "FloorDiv": "//",
    "Pow": "**"
}


binop = {
    name: eval(f"lambda a, b: a {op} b")
    for name, op in binop_s.items()}


op_to_dunder = {
    "Add": "add",
    "Mult": "mul",
    "MatMult": "matmul",
}


@attr.s(auto_attribs=True, hash=True)
class BinOpType(PynalyserType):
    op: str
    left: PynalyserType
    right: PynalyserType

    def __attrs_post_init__(self):
        left = self.left.deref()
        assert isinstance(left, SingleType)
        right = self.right.deref()
        assert isinstance(right, SingleType)

        def narrow_type(tp: SingleType, both: Tuple[str, str],
                        method: str, use_left: bool):
            if use_left:
                this_method = method
                other_method = "r" + method
            else:
                this_method = "r" + method
                other_method = method

            sign = tp.dunder_signatures.get(this_method, None)
            if sign is not None:
                # TODO: also add type that have __{other_method}__ op
                other = UnionType.make(*(
                    _tp()  # type: ignore
                    for _tp in sign))
                assert isinstance(other, SingleType)
            else:
                print(tp.dunder_signatures, method, sign)
                raise TypeError(
                    f"unsupported operand type(s) for {binop_s[self.op]}: "
                    f"'{both[0]}' and '{both[1]}'")

            return other

        if not left.is_completed and not right.is_completed:
            raise NotImplementedError
        elif not left.is_completed:
            left = narrow_type(
                right, (right.name, left.name),
                op_to_dunder[self.op], use_left=False)
        elif not right.is_completed:
            right = narrow_type(
                left, (left.name, right.name),
                op_to_dunder[self.op], use_left=True)
        # else:
        #     raise NotImplementedError
        #     name = op_to_dunder[op]
        #     lsig = left.dunder_signatures.get(name, None)
        #     if lsig is not None:
        #         if type(right) in lsig:
        #             return getattr(right, name)(left)

        #     name = "r" + name
        #     rsig = right.dunder_signatures.get(name, None)
        #     if rsig is not None:
        #         if type(left) in rsig:
        #             return getattr(left, name)(right)
        #     elif lsig is None:
        #         raise TypeError("")

        if isinstance(self.left, SymbolType):
            self.left.symbol.type = left
        if isinstance(self.right, SymbolType):
            self.right.symbol.type = right

    def deref(self) -> PynalyserType:
        return binop[self.op](self.left.deref(), self.right.deref())


cmp_s = {
    "Lt": "<",
    "Gt": ">",
}

cmp = {
    name: eval(f"lambda a, b: a {op} b")
    for name, op in cmp_s.items()}

cmp_to_dunder = {
    "Lt": "lt",
    "Gt": "gt",
}


@attr.s(auto_attribs=True, hash=True)
class CompareType(PynalyserType):
    left: PynalyserType
    ops: List[str]
    comparators: List[PynalyserType]

    def __attrs_post_init__(self):
        left = self.left.deref()
        assert isinstance(left, SingleType)
        right = self.comparators[0].deref()
        assert isinstance(right, SingleType)

        def narrow_type(tp: SingleType, both: Tuple[str, str],
                        method: str, use_left: bool):
            if use_left:
                this_method = method
                # other_method = "r" + method
                # swapped_cmp_op - lt <=> gt ..
            else:
                this_method = "r" + method
                # other_method = method

            sign = tp.dunder_signatures.get(this_method, None)
            if sign is not None:
                # TODO: also add type that have __{other_method}__ op
                other = UnionType.make(*(
                    _tp()  # type: ignore
                    for _tp in sign))
                assert isinstance(other, SingleType)
            else:
                print(tp.dunder_signatures, method, sign)
                raise TypeError(
                    f"unsupported operand type(s) for {cmp_s[self.ops[0]]}: "
                    f"'{both[0]}' and '{both[1]}'")

            return other

        if not left.is_completed and not right.is_completed:
            pass
            # raise NotImplementedError
        elif not left.is_completed:
            left = narrow_type(
                right, (right.name, left.name),
                cmp_to_dunder[self.ops[0]], use_left=False)
        elif not right.is_completed:
            right = narrow_type(
                left, (left.name, right.name),
                cmp_to_dunder[self.ops[0]], use_left=True)

        if isinstance(self.left, SymbolType):
            self.left.symbol.type = left
        if isinstance(self.comparators[0], SymbolType):
            self.comparators[0].symbol.type = right

    def _deref(self, res: PynalyserType, ops,
               vals: List[PynalyserType]) -> PynalyserType:
        if ops and vals:
            res = ops.pop(0)(res, vals.pop(0))
            if ops and vals:
                return self._deref(res, ops, vals)
            else:
                return res
        raise ValueError("Empty 'ops' and 'val'")

    def deref(self) -> PynalyserType:
        return self._deref(self.left, self.ops, self.comparators)


@attr.s(auto_attribs=True, hash=True)
class SubscriptType(PynalyserType):
    value: PynalyserType
    slice: PynalyserType

    def deref(self) -> PynalyserType:
        return self.value.deref()[self.slice.deref()]  # type: ignore

    # def visit_Subscript(self, node: ast.Subscript) -> PynalyserType:
    #     value_type = self.visit(node.value)
    #     slice_type = self.visit(node.slice)
    #     if isinstance(value_type, SequenceType):
    #         return value_type[slice_type]

    #     raise NotImplementedError


@attr.s(auto_attribs=True, hash=True)
class ItemType(PynalyserType):
    iterable: PynalyserType

    def __attrs_post_init__(self):
        tp = self.iterable.deref()
        if tp is UnknownType:
            if isinstance(self.iterable, SymbolType):
                self.iterable.symbol.type = IterableType(
                    item_type=UnknownType, is_builtin=False)
            # XXX: should we let it be and cause an error?
            # else:
            #     self.iterable = IterableType(
            #         item_type=UnknownType, is_builtin=False)

    def deref(self) -> PynalyserType:
        return self.iterable.deref().item_type.deref()  # type: ignore


@attr.s(auto_attribs=True, hash=True)
class CallType(PynalyserType):
    func: PynalyserType
    args: Tuple[PynalyserType, ...]
    keywords: Tuple[Tuple[Optional[str], PynalyserType], ...]

    def deref(self) -> PynalyserType:
        if isinstance(self.func, SymbolType) and self.func.name == "range":
            return IterableType(item_type=IntType(),
                                is_builtin=False)  # XXX: is_builtin??

        return AnyType
