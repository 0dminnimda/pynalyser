import ast
from typing import List, Union
from warnings import warn

from ..acr import classes as acr_c
from ..acr.utils import NodeVisitor, dump, NODE
from ._types import (DUNDER_SIGNATURE, IntType, PynalyserType, SequenceType,
                     SingleType, UnionType, AnyType)
from .tools import Analyser


# XXX: ACRExprTypeInference?
class CompTypeInference(NodeVisitor):
    # auto_global_visit: bool = True

    def infer(self, scope: acr_c.Scope, node: acr_c.ACR) -> PynalyserType:
        res = self.start(scope, node)
        if isinstance(res, PynalyserType):
            return res
        return AnyType

    def visit_ListComp(self, node: acr_c.ListComp) -> PynalyserType:
        return SequenceType(


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


class ASTExprTypeInference(ast.NodeVisitor):
    def infer(self, node: ast.AST) -> PynalyserType:
        res = self.visit(node)
        if isinstance(res, PynalyserType):
            return res
        return objectType
            name=list.__name__, item_type=AnyType, is_builtin=True)

    def visit_Attribute(self, node: ast.Attribute) -> PynalyserType:
        return AnyType

    def visit_BinOp(self, node: ast.BinOp) -> PynalyserType:
        return binop[type(node.op).__name__](
            self.visit(node.left), self.visit(node.right))

    def visit_List(self, node: ast.List) -> PynalyserType:
        return SequenceType(
            name=list.__name__, item_type=AnyType, is_builtin=True)

    def visit_Tuple(self, node: ast.Tuple) -> PynalyserType:
        return SequenceType(
            name=tuple.__name__, item_type=AnyType, is_builtin=True)

    def visit_Constant(self, node: ast.Constant) -> PynalyserType:
        if isinstance(node.value, int):
            return IntType()
        return SingleType(name=type(node.value).__name__, is_builtin=True)
        # warn("Inferring constant not as main type is not supported. "
        #      f"Main type is '{type(node).__name__}'")


class TypeInference(Analyser):
    comp_type_inference: CompTypeInference = CompTypeInference()
    ast_expr_type_inference: ASTExprTypeInference = ASTExprTypeInference()

    def infer_acr_expr(self, node: Union[ast.AST, acr_c.ACR]) -> PynalyserType:
        if isinstance(node, acr_c.ACR):
            return self.comp_type_inference.infer(self.scope, node)

        if isinstance(node, ast.AST):
            return self.ast_expr_type_inference.infer(node)

        raise TypeError(
            f"'node' should be AST or ACR, got {type(node).__name__}")

    def mash_ast_and_type(self, node: ast.AST, tp: PynalyserType) -> None:
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

        # elif isinstance(node, ast.Name):

    def visit_Assign(self, node: ast.Assign) -> None:
        tp = self.infer_acr_expr(node.value)
        for target in node.targets:
            self.mash_ast_and_type(target, tp)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value is not None:
            tp = self.infer_acr_expr(node.value)
            self.mash_ast_and_type(node.target, tp)
