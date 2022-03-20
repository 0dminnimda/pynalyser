import ast

from pynalyser.normalize_ast import AstNormalizer, normalize_ast


def assert_node_equality(node1: ast.AST, node2: ast.AST,
                         include_attributes: bool = False):
    assert (ast.dump(node1, include_attributes=include_attributes)
            == ast.dump(node2, include_attributes=include_attributes))


############ AstNormalizer #############

def normalized_node(node: ast.AST):
    return AstNormalizer().visit(node)


def test_visit_Num():
    assert_node_equality(normalized_node(ast.Num(69)),
                         ast.Constant(value=69))


def test_visit_Str():
    value = "use '<>' instead of '!=' (Barry)"
    assert_node_equality(normalized_node(ast.Str("")),
                         ast.Constant(value=""))
    assert_node_equality(normalized_node(ast.Str(value)),
                         ast.Constant(value=value))


def test_visit_Bytes():
    value = b"use '<>' instead of '!=' (Barry)"
    assert_node_equality(normalized_node(ast.Bytes(b"")),
                         ast.Constant(value=b""))
    assert_node_equality(normalized_node(ast.Bytes(value)),
                         ast.Constant(value=value))


def test_visit_NameConstant():
    assert_node_equality(normalized_node(ast.NameConstant(True)),
                         ast.Constant(value=True))
    assert_node_equality(normalized_node(ast.NameConstant(False)),
                         ast.Constant(value=False))
    assert_node_equality(normalized_node(ast.NameConstant(None)),
                         ast.Constant(value=None))


def test_visit_Ellipsis():
    assert_node_equality(normalized_node(ast.Ellipsis()),
                         ast.Constant(value=Ellipsis))
    assert_node_equality(normalized_node(ast.Ellipsis()),
                         ast.Constant(value=...))


def test_visit_Index():
    assert_node_equality(
        normalized_node(ast.Index(value=ast.Num(n=3))),
        ast.Constant(value=3))
    assert_node_equality(
        normalized_node(ast.Index(value=ast.Name(id='UnladenSwallow',
                                                 ctx=ast.Load()))),
        ast.Name(id='UnladenSwallow', ctx=ast.Load()))


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


############ normalize_ast #############

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
    assert_node_equality(normalized_source("number_of_the_counting[3]").slice,  # type: ignore
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
