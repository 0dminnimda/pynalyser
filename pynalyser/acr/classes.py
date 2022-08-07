from typing import List, Optional, Tuple, TypeVar, Union

import attr

from .. import ast

ACR_T = TypeVar("ACR_T")


@attr.s
class ACR:
    """The base class for each class of abstract representation of the code.
    Inherited classes can be dumped by :func:`acr.dump <pynalyser.acr.utils.dump>`,
    but for that to work properly inherited class should use `attr.s`.
    """

    _attributes: Tuple[str, ...] = attr.ib(init=False, default=())
    _fields: Tuple[str, ...] = attr.ib(init=False, default=())
    # _nonblock_fields: Tuple[str, ...] = ()
    # _block_fields: Tuple[str, ...] = attr.ib(init=False, default=())

    # XXX: abc ? from_ast, to_ast
    # @classmethod
    # def from_ast(cls: Type[ACR_T], node: ast.AST) -> ACR_T:
    #     raise NotImplementedError

    # FIXME: this should run only on class creation, so metaclasses?
    def __attrs_post_init__(self) -> None:
        _fields = list(attr.fields_dict(type(self)).keys())

        for name in self._attributes:
            _fields.remove(name)
        _fields.remove("_attributes")
        _fields.remove("_fields")

        self._fields = tuple(_fields)

        # _nonblock_fields = []
        # _block_fields = []  currently in Block


@attr.s(auto_attribs=True)
class Name(ACR):
    name: str
    is_symbol: bool = attr.ib(init=False, default=False)

    _attributes: Tuple[str, ...] = attr.ib(init=False, default=("is_symbol",))


@attr.s(auto_attribs=True)
class Asyncable(ACR):
    is_async: bool = attr.ib(kw_only=True)


CODE = Union[
    # stmt - from scope body
    ast.Delete, ast.Assign, ast.AugAssign, ast.AnnAssign,
    ast.Import, ast.ImportFrom,
    ast.Nonlocal, ast.Global,
    # Expr - no need for it
    ast.Pass,  # so blocks only with pass will be fine
    ast.Break, ast.Continue,

    # expr - from breakdown of complex expressions
    ast.BoolOp, ast.NamedExpr, ast.BinOp, ast.UnaryOp,
    ast.IfExp, ast.Dict, ast.Set, ast.Await,
    ast.Yield, ast.YieldFrom,  # special ones, can be removed later
    ast.Compare, ast.Call, ast.JoinedStr,
    # FormattedValue should not exist by itself (without JoinedStr)
    ast.Constant, ast.Attribute, ast.Subscript,
    # Starred should not exist by itself (without Call or Assign)
    ast.Name,  # the only use for that to exit by itself
    # is reporting a NameError: name 'xxx' is not defined
    ast.List, ast.Tuple,
    # Slice can appear only in Subscript

    # not ast
    "Scope"
]


CONTROL_FLOW = Union[  # TODO: not finished?
    "CodeBlock", "Block",

    # stmt - from scope body
    ast.Return, ast.Raise, ast.Assert,
    ast.Break, ast.Continue,

    # expr - from breakdown of complex expressions
    # ast.Yield, ast.YieldFrom for now it's in the CODE
]


# XXX: ControlFlowSomething? BlockContainer?
class FlowContainer(ACR, List[CONTROL_FLOW]):
    def get_code_block(self) -> "CodeBlock":
        if len(self):
            block = self[-1]
            if type(block) is not CodeBlock:
                block = CodeBlock()
                self.append(block)
        else:
            block = CodeBlock()
            self.append(block)

        return block

    def add_code(self, code: CODE) -> None:
        """Add code to latest block, if it's is not `CodeBlock`
        function will add new `CodeBlock` to `blocks` and add code there"""

        self.get_code_block().append(code)


class CodeBlock(ACR, List[CODE]):
    """a.k.a. Basic block"""
    pass


# @attr.s(auto_attribs=True)
class Block(ACR):
    _block_fields: Tuple[str, ...] = ()

    def __attrs_post_init__(self) -> None:
        super().__attrs_post_init__()
        _fields = list(self._fields)
        _fields.remove("_block_fields")
        self._fields = tuple(_fields)


@attr.s(auto_attribs=True)
class BodyBlock(Block):
    body: FlowContainer = attr.ib(factory=FlowContainer, init=False)
    _block_fields: Tuple[str, ...] = attr.ib(init=False, default=("body",))


@attr.s(auto_attribs=True)
class Scope(Name, BodyBlock):
    pass


class Module(Scope):
    """`name` is the name of the file that this module belongs to
    """
    # path?
    # XXX: is_symbol = True?
    pass


@attr.s(auto_attribs=True)
class ACRWithAttributes(ACR):
    lineno: int = attr.ib(kw_only=True)
    col_offset: int = attr.ib(kw_only=True)
    # TODO: make end_lineno and end_col_offset required fields
    # after switching to python-version-independent ast generator
    # (it will generate lastest ast for earlsier python versions)
    end_lineno: Optional[int] = attr.ib(default=None, kw_only=True)
    end_col_offset: Optional[int] = attr.ib(default=None, kw_only=True)

    _attributes: Tuple[str, ...] = attr.ib(init=False, default=(
        "lineno", "col_offset", "end_lineno", "end_col_offset"))


@attr.s(auto_attribs=True)
class ScopeWithAttributes(ACRWithAttributes, Scope):
    _attributes: Tuple[str, ...] = attr.ib(init=False, default=(
        "lineno", "col_offset", "end_lineno", "end_col_offset", "is_symbol"))


# we don't care about 'type_ignores'

@attr.s(auto_attribs=True)
class Class(ScopeWithAttributes):
    bases: List[ast.expr]  # parent-classes
    keywords: List[ast.keyword]  # initially metaclass and kws for it
    decorator_list: List[ast.expr]
    metaclass: Optional[type] = None  # XXX: it's probably not type really

    is_symbol: bool = attr.ib(init=False, default=True)


@attr.s(auto_attribs=True)
class Function(ScopeWithAttributes, Asyncable):
    args: ast.arguments = attr.ib(factory=ast.arguments)
    decorator_list: List[ast.expr] = attr.ib(factory=list)

    is_symbol: bool = attr.ib(init=False, default=True)


@attr.s(auto_attribs=True)
class Lambda(ScopeWithAttributes, ast.expr):
    name: str = attr.ib(default="<lambda>", init=False)
    args: ast.arguments = attr.ib(factory=ast.arguments)


@attr.s(auto_attribs=True)
class Comprehension(ScopeWithAttributes, ast.expr):
    # XXX: shouldn't have `body` from Scope,
    # but removing this will bring currently unneeded refactoring
    generators: List[ast.comprehension] = attr.ib(kw_only=True)
    _block_fields: Tuple[str, ...] = attr.ib(init=False, default=())


@attr.s(auto_attribs=True)
class EltComprehension(Comprehension):
    elt: ast.expr


@attr.s(auto_attribs=True)
class ListComp(EltComprehension):
    name: str = attr.ib(init=False, default="<listcomp>")


@attr.s(auto_attribs=True)
class SetComp(EltComprehension):
    name: str = attr.ib(init=False, default="<setcomp>")


@attr.s(auto_attribs=True)
class GeneratorExp(EltComprehension):
    name: str = attr.ib(init=False, default="<genexpr>")


@attr.s(auto_attribs=True)
class DictComp(Comprehension):
    key: ast.expr
    value: ast.expr
    name: str = attr.ib(init=False, default="<dictcomp>")


@attr.s(auto_attribs=True)
class MatchCase(BodyBlock):
    pattern: ast.pattern
    guard: Optional[ast.expr]


@attr.s(auto_attribs=True)
class Match(ACRWithAttributes, Block):
    subject: ast.expr
    cases: List[MatchCase] = attr.ib(init=False, factory=list)
    _block_fields: Tuple[str, ...] = attr.ib(init=False, default=("cases",))


@attr.s(auto_attribs=True)
class With(ACRWithAttributes, BodyBlock, Asyncable):
    items: List[ast.withitem]


@attr.s(auto_attribs=True)
class BodyElseBlock(BodyBlock):
    orelse: FlowContainer = attr.ib(factory=FlowContainer, init=False)
    _block_fields: Tuple[str, ...] = attr.ib(
        init=False, default=("body", "orelse"))


@attr.s(auto_attribs=True)
class If(ACRWithAttributes, BodyElseBlock):
    test: ast.expr


@attr.s(auto_attribs=True)
class ExceptHandler(ACRWithAttributes, BodyBlock):
    type: Optional[ast.expr]
    name: Optional[str]


@attr.s(auto_attribs=True)
class Try(ACRWithAttributes, BodyElseBlock):
    handlers: List[ExceptHandler] = attr.ib(factory=list, init=False)
    finalbody: FlowContainer = attr.ib(factory=FlowContainer, init=False)
    _block_fields: Tuple[str, ...] = attr.ib(
        init=False, default=("body", "handlers", "orelse", "finalbody"))


@attr.s(auto_attribs=True)
class Loop(ACRWithAttributes, BodyElseBlock):  # XXX: do we need this class?
    pass


@attr.s(auto_attribs=True)
class For(Loop, Asyncable):
    target: ast.expr  # ? Union[ast.Name, ast.Tuple, ast.List]
    iter: ast.expr


@attr.s(auto_attribs=True)
class While(Loop):
    test: ast.expr


# idea:
# class "list"
# def mark(index) -> id
# marked item's index will be tracked
# def get_index(id) -> index
