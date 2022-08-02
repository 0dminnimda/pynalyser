from typing import Any, Dict, Optional, cast
from . import portable_ast as ast

ATTRIBUTES = ("lineno", "col_offset")
OPTIONAL_ATTRIBUTES = ("end_lineno", "end_col_offset")


class AstNormalizer(ast.NodeTransformer):
    # we need to set all of the locations,
    # that's why ast.copy_location is not used
    def get_locations(self, node: ast.AST) -> Dict[str, Optional[int]]:
        result: Dict[str, Optional[int]] = {}

        for attr in ATTRIBUTES:
            value = getattr(node, attr)
            assert isinstance(value, int)
            result[attr] = value

        for attr in OPTIONAL_ATTRIBUTES:
            value = getattr(node, attr, None)
            assert isinstance(value, int) or value is None
            result[attr] = value

        return result

    def visit_Num(self, node: ast.Num) -> ast.Constant:
        return ast.Constant(node.n, **self.get_locations(node))

    def visit_Str(self, node: ast.Str) -> ast.Constant:
        return ast.Constant(node.s, **self.get_locations(node))

    def visit_Bytes(self, node: ast.Bytes) -> ast.Constant:
        return ast.Constant(node.s, **self.get_locations(node))

    def visit_NameConstant(self, node: ast.NameConstant) -> ast.Constant:
        return ast.Constant(node.value, **self.get_locations(node))

    def visit_Ellipsis(self, node: ast.Ellipsis) -> ast.Constant:
        return ast.Constant(..., **self.get_locations(node))

    def visit_Index(self, node: ast.Index) -> ast.AST:
        value = node.value  # type: ignore [name-defined]
        return self.visit(value)

    def visit_ExtSlice(self, node: ast.ExtSlice) -> ast.Tuple:
        dims = node.dims  # type: ignore [name-defined]
        return self.visit(ast.Tuple(dims, ast.Load()))
        # **self.get_locations(first node with locations from dims)

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
