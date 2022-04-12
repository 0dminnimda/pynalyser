import ast
import sys
from collections import defaultdict

from pynalyser.acr import classes as acr
# from pynalyser.acr import classes as acr
from pynalyser.acr.translation import Translator, translate_ast_to_acr
from pynalyser.acr.utils import dump

tree = ast.parse(
    # """
    # if x:
    #     a = 69 + 42
    # """)

    # (
    # """

    # # if a:
    # #     if b:
    # #         c
    # #     else:
    # #         d
    # # else:
    # #     if e:
    # #         f
    # #     else:
    # #         g

    # # try:
    # #     8
    # # except x:
    # #     6

    # # chain
    # # from itertools import chain as c

    # if x:
    #     a, b[0] = 5, 8
    # else:
    #     7



    # # @lambda x: x
    # # def t():
    # #     pass

    # # try:
    # #     9
    # # except y:
    # #     8

    # # if a:
    # #     def tt():
    # #         if h:
    # #             8
    # #         3
    # # else:
    # #     7
    # # 9

    # """)
    """
class T:
    7

class TT:
    def t():
        8

def a():
    5

def b():
    class B:
        0

def b():
    def c():
        2

69
""")

if sys.version_info >= (3, 9):
    print(ast.dump(tree, indent=4, include_attributes=True))

# print(acr.ScopeWithAttributes("", lineno=0, col_offset=4)._attributes)
# out = acr.Function(
#     name='b',
#     lineno=12,
#     col_offset=0)

# out.body.append(
#     acr.CodeBlock([
#         ast.Constant(
#             value=7,
#             kind=None,
#             lineno=3,
#             col_offset=4,
#             end_lineno=3,
#             end_col_offset=5)]))

# print(ast.NodeVisitor().visit(out))

out = translate_ast_to_acr(tree, "test")
print(dump(out, indent="|   ", include_attributes=True))

if sys.version_info < (3, 7):
    breakpoint = object

breakpoint

# acr.dump(f))  # out.scopes["a"][0]))
# f = out.blocks[0].body[0].value.get_scope(out)
quit()

# import attr

# @attr.s(auto_attribs=True)
# class T:
#     i: int

# t = T(5)
# print(attr.asdict(t),
#       attr.fields_dict(T),
#       attr.fields(T))
# del t.i
# print(attr.asdict(t))


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
    assert acr_module.body == []


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
