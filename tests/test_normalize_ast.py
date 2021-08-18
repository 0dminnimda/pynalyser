import ast

from pynalyser.normalize_ast import AstNormalizer, normalize_ast


def assert_node_equality(node1: ast.AST, node2: ast.AST):
    assert ast.dump(node1) == ast.dump(node2)


############ normalize_ast #############
# TODO: add a test that shows that ast.fix_missing_locations is in use,
# it is probably better to take tests for ast.fix_missing_locations from python sources.

def normalized_source(*args, **kwargs) -> ast.AST:
    tree = ast.parse(*args, **kwargs)
    return normalize_ast(tree).body[0].value


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
    assert_node_equality(normalized_source("number_of_the_counting[3]").slice,
                         ast.Constant(value=3, kind=None))
    assert_node_equality(
        normalized_source("airspeed_velocities[UnladenSwallow]").slice,
        ast.Name(id='UnladenSwallow', ctx=ast.Load()))


def test_normalize_ast_ExtSlice():
    assert_node_equality(normalized_source("pi[3:14, 15]").slice, ast.Tuple(
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
