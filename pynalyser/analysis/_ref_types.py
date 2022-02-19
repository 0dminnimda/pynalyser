from typing import Tuple
import attr

from ._types import PynalyserType, AnyType, SingleType, UnionType, IterableType
from .symbols import SymbolData


@attr.s(auto_attribs=True)
class SymbolType(PynalyserType):
    symbol: SymbolData

    def deref(self) -> PynalyserType:
        return self.symbol.type.deref()


binop_s = {"Add": "+",
           "Sub": "-",
           "Mult": "*",
           "MatMult": "@",
           "Div": "/",
           "Mod": "%",
           "LShift": "<<",
           "RShift": ">>",
           "BitOr": "|",
           "BitXor": "^",
           "BitAnd": "&",
           "FloorDiv": "//",
           "Pow": "**"}

binop = {
    name: eval(f"lambda a, b: a {op} b")
    for name, op in binop_s.items()}


op_to_dunder = {
    "Mult": "mul"
}


@attr.s(auto_attribs=True)
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
                other = UnionType.make(*sign)
                assert isinstance(other, SingleType)
            else:
                print(tp.dunder_signatures, method, sign)
                raise TypeError(
                    f"unsupported operand type(s) for {binop_s[self.op]}: "
                    f"'{both[0]}' and '{both[1]}'")

            return other

        if left is AnyType and right is AnyType:
            raise NotImplementedError
        elif left is AnyType:
            raise NotImplementedError
        elif right is AnyType:
            right = narrow_type(left, (left.name, right.name),
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


@attr.s(auto_attribs=True)
class SubscriptType(PynalyserType):
    value: PynalyserType
    slice: PynalyserType

    def deref(self) -> PynalyserType:
        return self.value.deref()[self.slice.deref()]

    # def visit_Subscript(self, node: ast.Subscript) -> PynalyserType:
    #     value_type = self.visit(node.value)
    #     slice_type = self.visit(node.slice)
    #     if isinstance(value_type, SequenceType):
    #         return value_type[slice_type]

    #     raise NotImplementedError


@attr.s(auto_attribs=True)
class ItemType(PynalyserType):
    iterable: PynalyserType

    def __attrs_post_init__(self):
        tp = self.iterable.deref()
        if tp is AnyType and isinstance(self.iterable, SymbolType):
            self.iterable.symbol.type = IterableType(
                item_type=AnyType, is_builtin=False)

    def deref(self) -> PynalyserType:
        return self.iterable.deref().item_type.deref()
