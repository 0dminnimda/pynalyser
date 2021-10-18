import ast
from typing import NoReturn, Union

from .classes import Function, Module, Scope, ScopeReference

STMT_SCOPE = Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef]


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

    def handle_scope(self, scope: Scope, node: ast.AST) -> ScopeReference:
        reference = self.scope.add_scope(scope)

        prev_scope, self.scope = self.scope, scope
        self.generic_visit(node)
        self.scope = prev_scope

        return reference

    def handle_stmt_scope(self, scope: Scope, node: STMT_SCOPE) -> None:
        self.scope.add_code(
            ast.Assign(targets=[ast.Name(id=scope.name)],
                       value=self.handle_scope(scope, node)))

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        self.handle_stmt_scope(
            Function(node.name, node.args, node.decorator_list),
            node)
        return node

    #### Transform the expressions ####

    # def visit_Lambda


def translate_ast_to_acr(tree: ast.Module, name: str) -> Module:
    return Translator().translate_from_module(tree, name)
