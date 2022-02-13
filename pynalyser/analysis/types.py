import ast
from typing import List, Union
from warnings import warn

from ..acr import classes as acr_c
from ..acr.utils import NodeVisitor, dump
from ._types import PynalyserType, UnionType, SingleType, IntType, SequenceType, objectType
from .tools import Analyser



class TypeInference(Analyser):
    def mash_ast_and_type(self, node: ast.AST, tp: PynalyserType) -> None:
        if isinstance(node, ast.Name):
            symbol_data = self.scope.symbol_table[node.id]
            if symbol_data.type is objectType:
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
