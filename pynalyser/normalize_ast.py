from typing import cast
from . import portable_ast as ast


class AstNormalizer(ast.NodeTransformer):
    def visit_Num(self, node: ast.Num) -> ast.Constant:
        return ast.Constant(node.n)

    def visit_Str(self, node: ast.Str) -> ast.Constant:
        return ast.Constant(node.s)

    def visit_Bytes(self, node: ast.Bytes) -> ast.Constant:
        return ast.Constant(node.s)

    def visit_NameConstant(self, node: ast.NameConstant) -> ast.Constant:
        return ast.Constant(node.value)

    def visit_Ellipsis(self, node: ast.Ellipsis) -> ast.Constant:
        return ast.Constant(...)

    def visit_Index(self, node: ast.Index) -> ast.AST:
        value = node.value  # type: ignore [name-defined]
        return self.visit(value)

    def visit_ExtSlice(self, node: ast.ExtSlice) -> ast.Tuple:
        dims = node.dims  # type: ignore [name-defined]
        return self.visit(ast.Tuple(dims, ast.Load()))

    # We are just getting rid of deprecated nodes,
    # so we don't need a warning (see: NodeTransformer.visit_Constant)
    # Same as NodeTransformer.visit(node) with visit_Constant removed
    def visit_Constant(self, node: ast.Constant) -> ast.Constant:
        return cast(ast.Constant, self.generic_visit(node))


def normalize_ast(tree: ast.AST) -> ast.AST:
    return ast.fix_missing_locations(AstNormalizer().visit(tree))


def normalize_ast_module(module: ast.Module) -> ast.Module:
    tree = normalize_ast(module)
    assert isinstance(tree, ast.Module)
    return tree
