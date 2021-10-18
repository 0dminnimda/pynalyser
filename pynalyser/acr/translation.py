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
        self.generic_visit(module)
        del self.scope, self.acr
        return acr

    # we don't care about 'type_ignores'

    def visit_Module(self, node: ast.Module) -> NoReturn:
        raise NotImplementedError(  # XXX: parsing error idk
            "Either you just called `visit` on the tree "
            "(which starts with `ast.Module`) - use `translate_from_module` "
            "or there's more than one `ast.Module` in the tree")
        # "ast.Module is handled in the translate_from_module "
        # "and there gotta be only one ast.Module in the tree")

    def visit_Expr(self, node: ast.Expr) -> ast.Expr:
        if type(node.value) in (ast.Yield, ast.YieldFrom):
            raise NotImplementedError(
                "implement handling of the Yield")  # TODO
        self.scope.add_code(node.value)
        # TODO: handle lambdas in the expr (everywhere, not only in the Expr)
        return node



def translate_ast_to_acr(tree: ast.Module, name: str) -> Module:
    return Translator().translate_from_module(tree, name)
