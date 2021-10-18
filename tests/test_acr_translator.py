import ast
import sys
from pynalyser.acr.translation import Translator, translate_ast_to_acr
from pynalyser.acr import classes as acr
from collections import defaultdict

tree = ast.parse("""
def a():
    5
69
""")
out = translate_ast_to_acr(tree, "test")
f = out.blocks[0].body[0].value.get_scope(out)


[
    ast.Expr(
        value=ast.BinOp(
            left=ast.Name(id='a', ctx=ast.Load()),
            op=ast.Add(),
            right=ast.Name(id='b', ctx=ast.Load())))]


def test_Module():
    tree = ast.Module(body=[], type_ignores=[])
    name = "test"
    acr_module = translate_ast_to_acr(tree, name)
    assert type(acr_module) == acr.Module
    assert acr_module.name == name
    assert acr_module.blocks == []
    assert acr_module.scopes == defaultdict(acr.ScopeDefs)
    assert acr_module.symbol_table == acr.SymbolTable()


def test_Expr():
    tree = ast.Module(
        body=[ast.Expr(value=ast.Name(id='a', ctx=ast.Load()))],
        type_ignores=[])
    acr_module = translate_ast_to_acr(tree, "test")
    # TODO
    breakpoint


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
