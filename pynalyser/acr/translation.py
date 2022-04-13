import sys
from typing import List, NoReturn, Optional, Union

from .. import portable_ast as ast
from ..analysis.symbol import ScopeType
from .classes import (Block, Class, DictComp, ExceptHandler, FlowContainer,
                      For, Function, GeneratorExp, If, Lambda, ListComp, Match,
                      MatchCase, Module, Scope, SetComp, Try, While, With)

STMT_SCOPE = Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef]


class ForBlocks(ast.AST):
    _fields = "blocks",
    blocks: FlowContainer


# XXX: restrict visit, so if there's no visit_x then raise exception
class Translator(ast.NodeTransformer):
    container: FlowContainer

    #### Transformations used only for expr scopes ####

    #### Blocks (all stmt) ####

    # XXX: we can shrink down ast.AST to smaller subset
    def handle_block_without_appending(
            self, block: Block, node: ast.AST) -> None:

        self.generic_visit(block)  # type: ignore

        self.handle_fields_of_block(block, node)

    def handle_fields_of_block(self, block: Block, node: ast.AST) -> None:
        prev_container = self.container

        for name in block._block_fields:
            value = getattr(node, name)
            some_container = getattr(block, name)  # FIXME: bad name!
            if isinstance(some_container, FlowContainer):
                self.container = some_container
                self.generic_visit(ForBlocks(value[:]))
                setattr(block, name, self.container)
            elif isinstance(some_container, list):
                # container should never be needed here
                for sub_container in value:
                    func = getattr(
                        self, "my_visit_" + type(sub_container).__name__)
                    some_container.append(func(sub_container))
            else:
                raise TypeError("All `_block_fields` should be subclasses "
                                "of the `list` or `FlowContainer`")

        self.container = prev_container

    def handle_block(self, block: Block, node: ast.AST) -> None:
        self.container.append(block)
        self.handle_block_without_appending(block, node)

    def visit_match_case(self, node: ast.match_case) -> ast.match_case:
        self.handle_block(
            MatchCase(node.pattern, node.guard),  # no attributes
            node)
        return node

    def visit_Match(self, node: ast.Match) -> ast.Match:
        self.handle_block(
            Match(node.subject,
                  lineno=node.lineno, col_offset=node.col_offset),
            node)
        return node

    def visit_With(self, node: ast.With) -> ast.With:
        self.handle_block(
            With(node.items, is_async=False,
                 lineno=node.lineno, col_offset=node.col_offset),
            node)
        return node

    def visit_AsyncWith(self, node: ast.AsyncWith) -> ast.AsyncWith:
        self.handle_block(
            With(node.items, is_async=True,
                 lineno=node.lineno, col_offset=node.col_offset),
            node)
        return node

    def visit_If(self, node: ast.If) -> ast.If:
        self.handle_block(
            If(node.test,
               lineno=node.lineno, col_offset=node.col_offset),
            node)
        return node

    def my_visit_ExceptHandler(self, node: ast.ExceptHandler) -> ExceptHandler:
        # should only be called from handle_block_without_appending
        acr_handler = ExceptHandler(
            node.type, node.name,
            lineno=node.lineno, col_offset=node.col_offset)
        self.handle_block_without_appending(acr_handler, node)
        return acr_handler

    def visit_Try(self, node: ast.Try) -> ast.Try:
        block = Try(lineno=node.lineno, col_offset=node.col_offset)
        self.handle_block(block, node)
        return node

    def visit_For(self, node: ast.For) -> ast.For:
        self.handle_block(
            For(node.target, node.iter, is_async=False,
                lineno=node.lineno, col_offset=node.col_offset),
            node)
        return node

    def visit_AsyncFor(self, node: ast.AsyncFor) -> ast.AsyncFor:
        self.handle_block(
            For(node.target, node.iter, is_async=True,
                lineno=node.lineno, col_offset=node.col_offset),
            node)
        return node

    def visit_While(self, node: ast.While) -> ast.While:
        self.handle_block(
            While(node.test,
                  lineno=node.lineno, col_offset=node.col_offset),
            node)
        return node

    #### expr scopes ####

    # XXX: we can shrink down node's ast.AST to smaller subset
    def handle_scope(self, scope: Scope, node: ast.AST) -> Scope:
        self.generic_visit(scope)  # type: ignore
        self.handle_fields_of_block(scope, node)
        return scope

    def visit_Lambda(self, node: ast.Lambda) -> Scope:
        lamb = Lambda(
            node.args, lineno=node.lineno, col_offset=node.col_offset)
        node.body = [ast.Expr(node.body)]  # type: ignore
        return self.handle_scope(lamb, node)

    def visit_ListComp(self, node: ast.ListComp) -> Scope:
        return self.handle_scope(
            ListComp(node.elt, generators=node.generators,
                     lineno=node.lineno, col_offset=node.col_offset),
            node)

    def visit_SetComp(self, node: ast.SetComp) -> Scope:
        return self.handle_scope(
            SetComp(node.elt, generators=node.generators,
                    lineno=node.lineno, col_offset=node.col_offset),
            node)

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> Scope:
        return self.handle_scope(
            GeneratorExp(node.elt, generators=node.generators,
                         lineno=node.lineno, col_offset=node.col_offset),
            node)

    def visit_DictComp(self, node: ast.DictComp) -> Scope:
        return self.handle_scope(
            DictComp(node.key, node.value, generators=node.generators,
                     lineno=node.lineno, col_offset=node.col_offset),
            node)

    #### stmt scopes ####

    def translate_from_module(self, module: ast.Module,
                              name: str) -> Module:
        acr = Module(name)
        self.container = acr.body
        self.generic_visit(module)
        del self.container
        return acr

    def visit_Module(self, node: ast.Module) -> NoReturn:
        raise NotImplementedError(  # XXX: parsing error idk
            "Either you just called `visit` on the tree "
            "(which starts with `ast.Module`) - use `translate_from_module` "
            "or there's more than one `ast.Module` in the tree")

    def handle_stmt_scope(self, scope: Scope, node: STMT_SCOPE) -> None:
        self.container.add_code(self.handle_scope(scope, node))

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        func = Function(
            node.name, node.args, node.decorator_list, is_async=False,
            lineno=node.lineno, col_offset=node.col_offset)
        self.handle_stmt_scope(func, node)
        return node

    def visit_AsyncFunctionDef(
        self, node: ast.AsyncFunctionDef
    ) -> ast.AsyncFunctionDef:

        func = Function(
            node.name, node.args, node.decorator_list, is_async=True,
            lineno=node.lineno, col_offset=node.col_offset)
        self.handle_stmt_scope(func, node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        self.handle_stmt_scope(
            Class(
                node.name, node.bases, node.keywords, node.decorator_list,
                lineno=node.lineno, col_offset=node.col_offset),
            node)
        return node

    #### Other contlow flow ####

    def visit_Return(self, node: ast.Return) -> ast.Return:
        self.generic_visit(node)
        self.container.append(node)
        return node

    def visit_Raise(self, node: ast.Raise) -> ast.Raise:
        self.generic_visit(node)
        self.container.append(node)
        return node

    def visit_Assert(self, node: ast.Assert) -> ast.Assert:
        self.generic_visit(node)
        self.container.append(node)
        return node

    def visit_Break(self, node: ast.Break) -> ast.Break:
        self.generic_visit(node)
        self.container.append(node)
        return node

    def visit_Continue(self, node: ast.Continue) -> ast.Continue:
        self.generic_visit(node)
        self.container.append(node)
        return node

    # TODO: handle yield
    # def visit_Yield(self, node: ast.Yield) -> ast.Yield:
    #     self.generic_visit(node)
    #     self.container.append(node)
    #     return node

    # TODO: handle yield from
    # def visit_YieldFrom(self, node: ast.YieldFrom) -> ast.YieldFrom:
    #     self.generic_visit(node)
    #     self.container.append(node)
    #     return node

    #### Leftover stmt-s ####

    def visit_Delete(self, node: ast.Delete) -> ast.Delete:
        self.generic_visit(node)
        self.container.add_code(node)
        return node

    def visit_Assign(self, node: ast.Assign) -> ast.Assign:
        self.generic_visit(node)
        self.container.add_code(node)
        return node

    def visit_AugAssign(self, node: ast.AugAssign) -> ast.AugAssign:
        self.generic_visit(node)
        self.container.add_code(node)
        return node

    def visit_AnnAssign(self, node: ast.AnnAssign) -> ast.AnnAssign:
        self.generic_visit(node)
        self.container.add_code(node)
        return node

    def visit_Import(self, node: ast.Import) -> ast.Import:
        self.generic_visit(node)
        self.container.add_code(node)
        return node

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom:
        self.generic_visit(node)
        self.container.add_code(node)
        return node

    def visit_Global(self, node: ast.Global) -> ast.Global:
        self.generic_visit(node)
        self.container.add_code(node)
        return node

    def visit_Nonlocal(self, node: ast.Nonlocal) -> ast.Nonlocal:
        self.generic_visit(node)
        self.container.add_code(node)
        return node

    def visit_Expr(self, node: ast.Expr) -> ast.Expr:
        self.generic_visit(node)
        self.container.add_code(node.value)  # type: ignore
        return node

    def visit_Pass(self, node: ast.Pass) -> ast.Pass:
        self.generic_visit(node)
        self.container.add_code(node)
        return node

    #### Leftover expr-s ####

    # BoolOp

    def visit_NamedExpr(self, node: ast.NamedExpr) -> ast.NamedExpr:
        self.generic_visit(node)
        self.container.add_code(node)
        return node

    # BinOp
    # UnaryOp

    # IfExp
    # Dict
    # Set

    # Await
    # Yield
    # YieldFrom

    # Compare
    # Call
    # FormattedValue
    # JoinedStr
    # Constant

    # Attribute
    # Subscript
    # Starred

    # Name

    # List
    # Tuple

    # Slice


def translate_ast_to_acr(tree: ast.Module, name: str) -> Module:
    return Translator().translate_from_module(tree, name)
