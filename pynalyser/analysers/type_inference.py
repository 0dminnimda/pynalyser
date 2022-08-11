from typing import Dict, Union

from .. import acr, ast
from ..types import (
    AnyType,
    BinOpType,
    CallType,
    CompareOpType,
    IntType,
    ItemType,
    ListType,
    PynalyserType,
    SingleType,
    SliceType,
    SubscriptType,
    SymbolType,
    TupleType,
    UnionType,
    UnknownType,
)
from .definitions import DefinitionAnalyser

BINOP: Dict[type, str] = {
    ast.Add: "add",
    ast.Sub: "sub",
    ast.MatMult: "matmul",
    ast.Mult: "mul",
    ast.Div: "truediv",
    ast.Mod: "mod",
    ast.LShift: "lshift",
    ast.RShift: "rshift",
    ast.BitOr: "or",
    ast.BitXor: "xor",
    ast.BitAnd: "and",
    ast.FloorDiv: "floordiv",
    ast.Pow: "pow",
}


CMPOP: Dict[type, str] = {
    ast.Eq: "eq",
    ast.NotEq: "ne",
    ast.Lt: "lt",
    ast.LtE: "le",
    ast.Gt: "gt",
    ast.GtE: "ge",
    ast.Is: "is",
    ast.IsNot: "is_not",
    ast.In: "contains",
    ast.NotIn: "contains_not",
}


UNOP: Dict[type, str] = {
    ast.Invert: "invert",
    ast.Not: "not",
    ast.UAdd: "pos",
    ast.USub: "neg",
}


class TypeInference(DefinitionAnalyser):
    auto_generic_visit: bool = False

    # Inferable expressions

    def visit_Call(self, node: ast.Call) -> PynalyserType:
        return CallType(
            self.visit(node.func),
            tuple(self.visit(item) for item in node.args),
            tuple((item.arg, self.visit(item.value)) for item in node.keywords),
        )

    # def visit_Attribute(self, node: ast.Attribute) -> PynalyserType:
    #     return AnyType

    def visit_Subscript(self, node: ast.Subscript) -> PynalyserType:
        return SubscriptType(self.visit(node.value), self.visit(node.slice))

    def visit_BinOp(self, node: ast.BinOp) -> PynalyserType:
        return BinOpType(
            self.visit(node.left), BINOP[type(node.op)], self.visit(node.right)
        )

    def visit_Compare(self, node: ast.Compare) -> PynalyserType:
        return CompareOpType(
            self.visit(node.left),
            [CMPOP[type(op)] for op in node.ops],
            [self.visit(item) for item in node.comparators],
        )

    ### Comprehentions ###

    def visit_ListComp(self, node: acr.ListComp) -> PynalyserType:
        return ListType(item_type=UnknownType)  # TODO: infer item type

    ### Builtin sequences ###

    def visit_List(self, node: ast.List) -> PynalyserType:
        return ListType(
            item_type=UnionType.make(*map(self.visit, node.elts), fallback=UnknownType)
        )

    def visit_Tuple(self, node: ast.Tuple) -> PynalyserType:
        return TupleType(
            item_type=UnionType.make(*map(self.visit, node.elts), fallback=UnknownType)
        )

    ### Basic "building blocks"  ###

    def visit_Slice(self, node: ast.Slice) -> PynalyserType:
        return SliceType()

    def visit_Constant(self, node: ast.Constant) -> PynalyserType:
        if isinstance(node.value, int):
            return IntType()
        return SingleType(name=type(node.value).__name__, is_builtin=True)

    def visit_Name(self, node: ast.Name) -> PynalyserType:
        return SymbolType(node.id, self.symtab[node.id].current_symbol)

    def infer_acr_expr(self, node: Union[ast.AST, acr.ACR]) -> PynalyserType:
        res = self.visit(node)
        if isinstance(res, PynalyserType):
            return res
        return AnyType

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

    ### Statements ###

    def visit_Assign(self, node: ast.Assign) -> None:
        tp = self.infer_acr_expr(node.value)
        for target in node.targets:
            self.infer_assignment(target, tp)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value is not None:
            tp = self.infer_acr_expr(node.value)
            self.infer_assignment(node.target, tp)

    def visit_For(self, node: acr.For) -> None:
        tp = self.infer_acr_expr(node.iter)
        self.infer_assignment(node.target, ItemType(tp))
        self.acr_generic_visit(node)

    def visit_While(self, node: acr.While) -> None:
        tp = self.infer_acr_expr(node.test)
        self.acr_generic_visit(node)
        # can be boolable
        # if bool(test) is always True / False,
        # then we have infinite loop or
        # we can skip loop

    # def visit_Function(self, node: acr.Function) -> None:
    #     self.scope.symbol_table[node.name]
