import ast
from typing import Union

from ..acr import classes as acr_c
from ..types import (AnyType, BinOpType, CallType, CompareType, IntType,
                     ItemType, ListType, PynalyserType, SingleType, SliceType,
                     SubscriptType, SymbolType, TupleType, UnionType,
                     UnknownType)
from .scope import SymTabAnalyser


class TypeInference(SymTabAnalyser):
    # Inferable expressions

    def visit_Call(self, node: ast.Call) -> PynalyserType:
        return CallType(
            self.visit(node.func),
            tuple(self.visit(item) for item in node.args),
            tuple((item.arg, self.visit(item.value)) for item in node.keywords)
        )

    # def visit_Attribute(self, node: ast.Attribute) -> PynalyserType:
    #     return AnyType

    def visit_Subscript(self, node: ast.Subscript) -> PynalyserType:
        return SubscriptType(self.visit(node.value), self.visit(node.slice))

    def visit_BinOp(self, node: ast.BinOp) -> PynalyserType:
        return BinOpType(type(node.op).__name__,
                         self.visit(node.left), self.visit(node.right))

    def visit_Compare(self, node: ast.Compare) -> PynalyserType:
        return CompareType(self.visit(node.left),
                           [type(op).__name__ for op in node.ops],
                           [self.visit(item) for item in node.comparators])

    ### Comprehentions ###

    def visit_ListComp(self, node: acr_c.ListComp) -> PynalyserType:
        return ListType(item_type=UnknownType)  # TODO: infer item type

    ### Builtin sequences ###

    def visit_List(self, node: ast.List) -> PynalyserType:
        return ListType(item_type=UnionType.make(
            *map(self.visit, node.elts), fallback=UnknownType))

    def visit_Tuple(self, node: ast.Tuple) -> PynalyserType:
        return TupleType(item_type=UnionType.make(
            *map(self.visit, node.elts), fallback=UnknownType))

    ### Basic "building blocks"  ###

    def visit_Slice(self, node: ast.Slice) -> PynalyserType:
        return SliceType()

    def visit_Constant(self, node: ast.Constant) -> PynalyserType:
        if isinstance(node.value, int):
            return IntType()
        return SingleType(name=type(node.value).__name__, is_builtin=True)

    def visit_Name(self, node: ast.Name) -> PynalyserType:
        return SymbolType(node.id, self.symtab[node.id])

    # def infer(self, scope: acr_c.Scope, node: NODE) -> PynalyserType:
    #     res = self.start(scope, node)
    #     if isinstance(res, PynalyserType):
    #         return res
    #     return AnyType

    def infer_acr_expr(self, node: Union[ast.AST, acr_c.ACR]) -> PynalyserType:
        # res = self.start(node, node)
        res = self.visit(node)
        if isinstance(res, PynalyserType):
            return res
        return AnyType
        # return self.expr_type_inference.infer(self.scope, node)

    def infer_assignment(self, node: ast.AST, tp: PynalyserType) -> None:
        if isinstance(node, ast.Name):
            symbol_data = self.symtab[node.id]
            if symbol_data.type is UnknownType:
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
        self.infer_assignment(node.target, ItemType(tp))

    def visit_While(self, node: acr_c.While) -> None:
        tp = self.infer_acr_expr(node.test)
        # can be boolable
        # if bool(test) is always True / False,
        # then we have infinite loop or
        # we can skip loop
