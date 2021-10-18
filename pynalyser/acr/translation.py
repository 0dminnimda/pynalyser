import ast
from typing import NoReturn, Union

from .classes import Function, Module, Scope, ScopeReference


class Translator(ast.NodeTransformer):
    acr: Module
    scope: Scope

    #### Only visit, no transformations ####

    def translate_from_module(self, module: ast.Module,
                              name: str) -> Module:
        acr = self.scope = self.acr = Module(name)
        self.generic_visit(module)  # we don't care about 'type_ignores'
        self.acr = None
        return acr

    def visit_Module(self, node: ast.Module) -> NoReturn:
        raise NotImplementedError(  # XXX: parsing error idk
            "ast.Module is handled in the translate_from_module")

    def visit_Expr(self, node: ast.Expr) -> None:
        self.scope.body.append(node.value)


def translate_ast_to_acr(tree: ast.Module, name: str) -> Module:
    return Translator().translate_from_module(tree, name)
