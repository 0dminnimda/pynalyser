import sys
import typing
from ast import *

# backports
if sys.version_info < (3, 10):
    class pattern(AST):
        ...

    class match_case(AST):
        pattern: pattern
        guard: typing.Optional[expr]
        body: typing.List[stmt]
        _fields = ("pattern", "guard", "body")

    class Match(stmt):
        subject: expr
        cases: typing.List[match_case]
        _fields = ("subject", "cases")

if sys.version_info < (3, 8):
    class NamedExpr(expr):
        target: expr
        value: Expr
        _fields = ("target", "value")


# TODO: Create dummy classes for ast.Num, ast.Str, ast.Bytes,
# ast.NameConstant, ast.Ellipsis, ast.Index and ast.ExtSlice
# for the version where they will be removed
# and add them to ast
# (For the purposes of correct type checking and
# maintaining consistent content of the module ast)

# TODO: build python parser from for the newest version of cpython
# and ship it in a separate package to be python version independent
# or use other python parsers

# clean up the namespace
# this module is supposed to be imported via the star
del sys, typing
