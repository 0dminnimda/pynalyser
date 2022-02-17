import ast
from typing import List, Tuple, Union
from warnings import warn

from ..acr import classes as acr_c
from ..acr.utils import NODE, NodeVisitor, dump
from ._types import (DUNDER_SIGNATURE, AnyType, IntType, PynalyserType,
                     SequenceType, SingleType, UnionType, ListType, SliceType)
from .tools import Analyser

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
    "*": "mul"
}


class ExprTypeInference(NodeVisitor):
    # auto_global_visit: bool = True

    def infer(self, scope: acr_c.Scope, node: NODE) -> PynalyserType:
        res = self.start(scope, node)
        if isinstance(res, PynalyserType):
            return res
        return AnyType

    def visit_ListComp(self, node: acr_c.ListComp) -> PynalyserType:
        return ListType(item_type=AnyType)  # TODO: infer item type

    def visit_Attribute(self, node: ast.Attribute) -> PynalyserType:
        return AnyType

    def visit_Subscript(self, node: ast.Subscript) -> PynalyserType:
        value_type = self.visit(node.value)
        slice_type = self.visit(node.slice)
        if isinstance(value_type, SequenceType):
            return value_type[slice_type]

        raise NotImplementedError

    def visit_Slice(self, node: ast.Slice) -> PynalyserType:
        return SliceType()

    def visit_BinOp(self, node: ast.BinOp) -> PynalyserType:
        left, right, result = self.handle_op(
            type(node.op).__name__,
            self.visit(node.left), self.visit(node.right))

        if isinstance(node.left, ast.Name):
            self.scope.symbol_table[node.left.id].type = left
        if isinstance(node.right, ast.Name):
            self.scope.symbol_table[node.right.id].type = right

        return result

    def visit_List(self, node: ast.List) -> PynalyserType:
        return ListType(item_type=UnionType.make(
            *map(self.visit, node.elts), fallback=AnyType))

    def visit_Tuple(self, node: ast.Tuple) -> PynalyserType:
        return SequenceType(name=tuple.__name__, is_builtin=True,
                            item_type=UnionType.make(
                                *map(self.visit, node.elts), fallback=AnyType))

    def visit_Constant(self, node: ast.Constant) -> PynalyserType:
        if isinstance(node.value, int):
            return IntType()
        return SingleType(name=type(node.value).__name__, is_builtin=True)

    def visit_Name(self, node: ast.Name) -> PynalyserType:
        return self.scope.symbol_table[node.id].type

    def handle_op(
        self, op: str, left: SingleType, right: SingleType
    ) -> Tuple[SingleType, SingleType, SingleType]:

        if left is AnyType and right is AnyType:
            raise NotImplementedError
        elif left is AnyType:
            raise NotImplementedError
        elif right is AnyType:
            lsig = left.dunder_signatures.get(op_to_dunder[binop_s[op]], None)
            if lsig is not None:
                # TODO: also add type that have __rX__ op
                right = UnionType.make(*lsig)
                assert isinstance(right, SingleType)
            else:
                print(left.dunder_signatures, op_to_dunder[binop_s[op]], lsig)
                raise TypeError(
                    f"unsupported operand type(s) for {binop_s[op]}: "
                    f"'{left.name}' and '{right.name}'")
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

        return left, right, binop[op](left, right)


class TypeInference(Analyser):
    expr_type_inference: ExprTypeInference = ExprTypeInference()

    def infer_acr_expr(self, node: Union[ast.AST, acr_c.ACR]) -> PynalyserType:
        return self.expr_type_inference.infer(self.scope, node)

    def infer_assignment(self, node: ast.AST, tp: PynalyserType) -> None:
        if isinstance(node, ast.Name):
            symbol_data = self.scope.symbol_table[node.id]
            if symbol_data.type is AnyType:
                symbol_data.type = tp
            else:
                symbol_data.type = UnionType.make(symbol_data.type, tp)
                # XXX: ideally we have to create
                # new variables-clones for type changes
                # anyways it's not handled here
                # raise TypeError("symbol's type is already set to {}")

        # in case of list or tuple we can infer number of elements
        # elif isinstance(node, ast.Name):

    def visit_Assign(self, node: ast.Assign) -> None:
        tp = self.infer_acr_expr(node.value)
        for target in node.targets:
            self.infer_assignment(target, tp)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value is not None:
            tp = self.infer_acr_expr(node.value)
            self.infer_assignment(node.target, tp)

    def visit_For(self, node: acr_c.For) -> None:
        tp = self.infer_acr_expr(node.iter)

        # TODO: BAD CODE, WE NEED IterableType
        try:
            tp = tp.item_type
        except AttributeError:
            pass

        self.infer_assignment(node.target, tp)
