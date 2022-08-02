import ast
import sys
from typing import cast

from pynalyser.ast import AstNormalizer, normalize_ast


def assert_node_equality(node1: ast.AST, node2: ast.AST, attributes: bool = False):
    assert ast.dump(node1, include_attributes=attributes) == ast.dump(
        node2, include_attributes=attributes
    )


USE_STR = "use '<>' instead of '!='"
USE_BYTES = USE_STR.encode()

nodes = dict(
    Num=(
        "42",
        ast.Num(n=42, lineno=1, col_offset=0, end_lineno=1, end_col_offset=2),
        ast.Constant(value=42, lineno=1, col_offset=0, end_lineno=1, end_col_offset=2),
    ),
    Str1=(
        "''",
        ast.Str(s="", lineno=1, col_offset=0, end_lineno=1, end_col_offset=2),
        ast.Constant(value="", lineno=1, col_offset=0, end_lineno=1, end_col_offset=2),
    ),
    Str2=(
        repr(USE_STR),
        ast.Str(s=USE_STR, lineno=1, col_offset=0, end_lineno=1, end_col_offset=26),
        ast.Constant(
            value=USE_STR, lineno=1, col_offset=0, end_lineno=1, end_col_offset=26
        ),
    ),
    Bytes1=(
        "b''",
        ast.Bytes(s=b"", lineno=1, col_offset=0, end_lineno=1, end_col_offset=3),
        ast.Constant(value=b"", lineno=1, col_offset=0, end_lineno=1, end_col_offset=3),
    ),
    Bytes2=(
        repr(USE_BYTES),
        ast.Bytes(s=USE_BYTES, lineno=1, col_offset=0, end_lineno=1, end_col_offset=27),
        ast.Constant(
            value=USE_BYTES, lineno=1, col_offset=0, end_lineno=1, end_col_offset=27
        ),
    ),
    NameConstant1=(
        "True",
        ast.NameConstant(
            value=True, lineno=1, col_offset=0, end_lineno=1, end_col_offset=4
        ),
        ast.Constant(
            value=True, lineno=1, col_offset=0, end_lineno=1, end_col_offset=4
        ),
    ),
    NameConstant2=(
        "False",
        ast.NameConstant(
            value=False, lineno=1, col_offset=0, end_lineno=1, end_col_offset=5
        ),
        ast.Constant(
            value=False, lineno=1, col_offset=0, end_lineno=1, end_col_offset=5
        ),
    ),
    NameConstant3=(
        "None",
        ast.NameConstant(
            value=None, lineno=1, col_offset=0, end_lineno=1, end_col_offset=4
        ),
        ast.Constant(
            value=None, lineno=1, col_offset=0, end_lineno=1, end_col_offset=4
        ),
    ),
    Ellipsis1=(
        "...",
        ast.Ellipsis(lineno=1, col_offset=0, end_lineno=1, end_col_offset=3),
        ast.Constant(
            value=Ellipsis, lineno=1, col_offset=0, end_lineno=1, end_col_offset=3
        ),
    ),
    Ellipsis2=(
        "...",
        ast.Ellipsis(lineno=1, col_offset=0, end_lineno=1, end_col_offset=3),
        ast.Constant(value=..., lineno=1, col_offset=0, end_lineno=1, end_col_offset=3),
    ),
    Index1=(
        "the_numbers_thou_shalt_count [ 3 ]",
        ast.Subscript(
            value=ast.Name(
                id="the_numbers_thou_shalt_count",
                ctx=ast.Load(),
                lineno=1,
                col_offset=0,
                end_lineno=1,
                end_col_offset=28,
            ),
            slice=ast.Index(
                value=ast.Num(
                    n=3, lineno=1, col_offset=31, end_lineno=1, end_col_offset=32
                )
            ),
            ctx=ast.Load(),
            lineno=1,
            col_offset=0,
            end_lineno=1,
            end_col_offset=34,
        ),
        ast.Subscript(
            value=ast.Name(
                id="the_numbers_thou_shalt_count",
                ctx=ast.Load(),
                lineno=1,
                col_offset=0,
                end_lineno=1,
                end_col_offset=28,
            ),
            slice=ast.Constant(
                value=3, lineno=1, col_offset=31, end_lineno=1, end_col_offset=32
            ),
            ctx=ast.Load(),
            lineno=1,
            col_offset=0,
            end_lineno=1,
            end_col_offset=34,
        ),
    ),
    Index2=(
        "airspeed_velocities [ UnladenSwallow ]",
        ast.Subscript(
            value=ast.Name(
                id="airspeed_velocities",
                ctx=ast.Load(),
                lineno=1,
                col_offset=0,
                end_lineno=1,
                end_col_offset=19,
            ),
            slice=ast.Index(
                value=ast.Name(
                    id="UnladenSwallow",
                    ctx=ast.Load(),
                    lineno=1,
                    col_offset=22,
                    end_lineno=1,
                    end_col_offset=36,
                )
            ),
            ctx=ast.Load(),
            lineno=1,
            col_offset=0,
            end_lineno=1,
            end_col_offset=38,
        ),
        ast.Subscript(
            value=ast.Name(
                id="airspeed_velocities",
                ctx=ast.Load(),
                lineno=1,
                col_offset=0,
                end_lineno=1,
                end_col_offset=19,
            ),
            slice=ast.Name(
                id="UnladenSwallow",
                ctx=ast.Load(),
                lineno=1,
                col_offset=22,
                end_lineno=1,
                end_col_offset=36,
            ),
            ctx=ast.Load(),
            lineno=1,
            col_offset=0,
            end_lineno=1,
            end_col_offset=38,
        ),
    ),
    ExtSlice=(
        "pi [ 3 : 14, 15 ]",
        ast.Subscript(
            value=ast.Name(
                id="pi",
                ctx=ast.Load(),
                lineno=1,
                col_offset=0,
                end_lineno=1,
                end_col_offset=2,
            ),
            slice=ast.ExtSlice(
                dims=[
                    ast.Slice(
                        lower=ast.Num(
                            n=3,
                            lineno=1,
                            col_offset=5,
                            end_lineno=1,
                            end_col_offset=6,
                        ),
                        upper=ast.Num(
                            n=14,
                            lineno=1,
                            col_offset=9,
                            end_lineno=1,
                            end_col_offset=11,
                        ),
                        step=None,
                        lineno=1,
                        col_offset=5,
                        end_lineno=1,
                        end_col_offset=11,
                    ),
                    ast.Index(
                        value=ast.Num(
                            n=15,
                            lineno=1,
                            col_offset=13,
                            end_lineno=1,
                            end_col_offset=15,
                        )
                    ),
                ]
            ),
            ctx=ast.Load(),
            lineno=1,
            col_offset=0,
            end_lineno=1,
            end_col_offset=17,
        ),
        ast.Subscript(
            value=ast.Name(
                id="pi",
                ctx=ast.Load(),
                lineno=1,
                col_offset=0,
                end_lineno=1,
                end_col_offset=2,
            ),
            slice=ast.Tuple(
                elts=[
                    ast.Slice(
                        lower=ast.Constant(
                            value=3,
                            lineno=1,
                            col_offset=5,
                            end_lineno=1,
                            end_col_offset=6,
                        ),
                        upper=ast.Constant(
                            value=14,
                            lineno=1,
                            col_offset=9,
                            end_lineno=1,
                            end_col_offset=11,
                        ),
                        step=None,
                        lineno=1,
                        col_offset=5,
                        end_lineno=1,
                        end_col_offset=11,
                    ),
                    ast.Constant(
                        value=15,
                        lineno=1,
                        col_offset=13,
                        end_lineno=1,
                        end_col_offset=15,
                    ),
                ],
                ctx=ast.Load(),
                lineno=1,
                col_offset=5,
                end_lineno=1,
                end_col_offset=15,
            ),
            ctx=ast.Load(),
            lineno=1,
            col_offset=0,
            end_lineno=1,
            end_col_offset=17,
        ),
    ),
)


############ AstNormalizer #############


def normalized_node(node: ast.AST) -> ast.AST:
    return AstNormalizer().visit(node)


def check_node(source: str, deprecated_node: ast.AST, node: ast.AST) -> None:
    assert_node_equality(normalized_node(deprecated_node), node, True)


if sys.version < "3.8":

    def test_visit_Num():
        check_node(*nodes["Num"])


def test_visit_Str():
    check_node(*nodes["Str1"])
    check_node(*nodes["Str2"])


def test_visit_Bytes():
    check_node(*nodes["Bytes1"])
    check_node(*nodes["Bytes2"])


def test_visit_NameConstant():
    check_node(*nodes["NameConstant1"])
    check_node(*nodes["NameConstant2"])
    check_node(*nodes["NameConstant3"])


def test_visit_Ellipsis():
    check_node(*nodes["Ellipsis1"])
    check_node(*nodes["Ellipsis2"])


if sys.version < "3.9":

    def test_visit_Index():
        check_node(*nodes["Index1"])
        check_node(*nodes["Index2"])

    def test_visit_ExtSlice():
        return  # for now
        check_node(*nodes["ExtSlice"])


############ normalize_ast #############


def normalized_source(source: str) -> ast.AST:
    tree = normalize_ast(ast.parse(source, mode="eval"))
    return cast(ast.Expression, tree).body


def check_source(source: str, deprecated_node: ast.AST, node: ast.AST) -> None:
    assert_node_equality(normalized_source(source), node, True)


def test_normalize_ast_Num():
    check_source(*nodes["Num"])


def test_normalize_ast_Str():
    check_source(*nodes["Str1"])
    check_source(*nodes["Str2"])


def test_normalize_ast_Bytes():
    check_source(*nodes["Bytes1"])
    check_source(*nodes["Bytes2"])


def test_normalize_ast_NameConstant():
    check_source(*nodes["NameConstant1"])
    check_source(*nodes["NameConstant2"])
    check_source(*nodes["NameConstant3"])


def test_normalize_ast_Ellipsis():
    check_source(*nodes["Ellipsis1"])
    check_source(*nodes["Ellipsis2"])


def test_normalize_ast_Index():
    check_source(*nodes["Index1"])
    check_source(*nodes["Index2"])


def test_normalize_ast_ExtSlice():
    check_source(*nodes["ExtSlice"])


if __name__ == "__main__":
    import pytest

    pytest.main([__file__])
