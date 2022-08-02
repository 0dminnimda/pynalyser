import ast

from pynalyser.ast import AstNormalizer, normalize_ast


def assert_node_equality(node1: ast.AST, node2: ast.AST,
                         include_attributes: bool = False):
    assert (ast.dump(node1, include_attributes=include_attributes)
            == ast.dump(node2, include_attributes=include_attributes))


############ AstNormalizer #############

def normalized_node(node: ast.AST):
    return AstNormalizer().visit(node)


def check_node(node1: ast.AST, node2: ast.AST):
    assert_node_equality(normalized_node(node1), node2)


USE_STR = "use '<>' instead of '!='"
USE_BYTES = b"use '<>' instead of '!='"

nodes = dict(
    Num=(
        ast.Num(42, lineno=1, col_offset=0),
        ast.Constant(value=42, lineno=1, col_offset=0)),
    Str1=(
        ast.Str("", lineno=1, col_offset=0),
        ast.Constant(value="", lineno=1, col_offset=0)),
    Str2=(
        ast.Str(USE_STR, lineno=1, col_offset=0),
        ast.Constant(value=USE_STR, lineno=1, col_offset=0)),
    Bytes1=(
        ast.Bytes(b"", lineno=1, col_offset=0),
        ast.Constant(value=b"", lineno=1, col_offset=0)),
    Bytes2=(
        ast.Bytes(USE_BYTES, lineno=1, col_offset=0),
        ast.Constant(value=USE_BYTES, lineno=1, col_offset=0)),
    NameConstant1=(
        ast.NameConstant(True, lineno=1, col_offset=0),
        ast.Constant(value=True, lineno=1, col_offset=0)),
    NameConstant2=(
        ast.NameConstant(False, lineno=1, col_offset=0),
        ast.Constant(value=False, lineno=1, col_offset=0)),
    NameConstant3=(
        ast.NameConstant(None, lineno=1, col_offset=0),
        ast.Constant(value=None, lineno=1, col_offset=0)),
    Ellipsis1=(
        ast.Ellipsis(lineno=1, col_offset=0),
        ast.Constant(value=Ellipsis, lineno=1, col_offset=0)),
    Ellipsis2=(
        ast.Ellipsis(lineno=1, col_offset=0),
        ast.Constant(value=..., lineno=1, col_offset=0)),
)


if sys.version < "3.8":
    def test_visit_Num():
        check_node(*nodes.pop("Num"))


def test_visit_Str():
    check_node(*nodes.pop("Str1"))
    check_node(*nodes.pop("Str2"))


def test_visit_Bytes():
    check_node(*nodes.pop("Bytes1"))
    check_node(*nodes.pop("Bytes2"))


def test_visit_NameConstant():
    check_node(*nodes.pop("NameConstant1"))
    check_node(*nodes.pop("NameConstant2"))
    check_node(*nodes.pop("NameConstant3"))


def test_visit_Ellipsis():
def test_visit_Index():
    assert_node_equality(
        normalized_node(ast.Index(value=ast.Num(n=3))),
        ast.Constant(value=3))
    assert_node_equality(
        normalized_node(ast.Index(value=ast.Name(id='UnladenSwallow',
                                                 ctx=ast.Load()))),
        ast.Name(id='UnladenSwallow', ctx=ast.Load()))
    check_node(*nodes.pop("Ellipsis1"))
    check_node(*nodes.pop("Ellipsis2"))




def test_visit_ExtSlice():
    ext_slice = ast.ExtSlice(dims=[
        ast.Slice(lower=ast.Num(n=3), upper=ast.Num(n=14)),
        ast.Index(value=ast.Num(n=15))
    ])

    assert_node_equality(
        normalized_node(ext_slice),
        ast.Tuple(
            elts=[
                ast.Slice(
                    lower=ast.Constant(value=3),
                    upper=ast.Constant(value=14)),
                ast.Constant(value=15),
            ],
            ctx=ast.Load()
        )
    )
def test_that_we_used_every_node():
    assert len(nodes) == 0


############ normalize_ast #############

def normalized_source(*args, **kwargs) -> ast.AST:
    tree = ast.parse(*args, **kwargs)
    return normalize_ast(tree).body[0].value  # type: ignore


def test_normalize_ast_Num():
    assert_node_equality(normalized_source("42"),
                         ast.Constant(value=42, kind=None))


def test_normalize_ast_Str():
    value = "The quick brown fox jumps over the lazy dog"
    assert_node_equality(normalized_source("''"),
                         ast.Constant(value="", kind=None))
    assert_node_equality(normalized_source(repr(value)),
                         ast.Constant(value=value, kind=None))


def test_normalize_ast_Bytes():
    value = b"The quick brown fox jumps over the lazy dog"
    assert_node_equality(normalized_source("b''"),
                         ast.Constant(value=b"", kind=None))
    assert_node_equality(normalized_source(repr(value)),
                         ast.Constant(value=value, kind=None))


def test_normalize_ast_NameConstant():
    assert_node_equality(normalized_source("True"),
                         ast.Constant(value=True, kind=None))
    assert_node_equality(normalized_source("False"),
                         ast.Constant(value=False, kind=None))
    assert_node_equality(normalized_source("None"),
                         ast.Constant(value=None, kind=None))


def test_normalize_ast_Ellipsis():
    assert_node_equality(normalized_source("..."),
                         ast.Constant(value=Ellipsis, kind=None))
    assert_node_equality(normalized_source("..."),
                         ast.Constant(value=..., kind=None))


def test_normalize_ast_Index():
    assert_node_equality(
        normalized_source("number_of_the_counting[3]").slice,  # type: ignore
        ast.Constant(value=3, kind=None))
    id = "UnladenSwallow"
    assert_node_equality(
        normalized_source(f"airspeed_velocities[{id}]").slice,  # type: ignore
        ast.Name(id=id, ctx=ast.Load()))


def test_normalize_ast_ExtSlice():
    assert_node_equality(
        normalized_source("pi[3:14, 15]").slice,  # type: ignore
        ast.Tuple(
            elts=[
                ast.Slice(
                    lower=ast.Constant(value=3, kind=None),
                    upper=ast.Constant(value=14, kind=None),
                    step=None),
                ast.Constant(value=15, kind=None),
            ],
            ctx=ast.Load()))


if __name__ == "__main__":
    import pytest

    pytest.main()
