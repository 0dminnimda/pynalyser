import ast
import sys
from abc import ABC, abstractmethod
from collections import defaultdict
from enum import Flag, auto
from typing import (Any, Callable, Collection, DefaultDict, Dict, FrozenSet,
                    Iterable, Iterator, List, NamedTuple, Optional, Tuple,
                    Type, TypeVar, Union)

import attr

from ..types.classes import PynalyserType, objectType

# XXX
if sys.version_info < (3, 10):
    class ast_pattern(ast.AST):
        pass
else:
    ast_pattern = ast.pattern

if sys.version_info < (3, 8):
    class ast_NamedExpr(ast.expr):
        target: ast.expr
        value: ast.expr
else:
    ast_NamedExpr = ast.NamedExpr


# XXX
if sys.version_info < (3, 10):
    ast_pattern = ast.AST
else:
    ast_pattern = ast.pattern

if sys.version_info < (3, 8):
    ast_NamedExpr = ast.AST
else:
    ast_NamedExpr = ast.NamedExpr


ACR_T = TypeVar("ACR_T")


@attr.s
class ACR:
    """The base class for each class of abstract representation of the code.
    Inherited classes could be dumpable by `acr.dump`,
    but for that to work properly inherited class should use `attr.s`.
    """

    _attributes: Tuple[str, ...] = attr.ib(init=False, default=())
    _fields: Tuple[str, ...] = attr.ib(init=False, default=())
    # _nonblock_fields: Tuple[str, ...] = ()
    # _block_fields: Tuple[str, ...] = attr.ib(init=False, default=())

    # @abstractmethod
    # def _format(self, ctx: Context, lvl: int) -> Tuple[List[str], bool]:
    #     ...
    # TODO: abc ? from_ast, to_ast

    @classmethod
    def from_ast(cls: Type[ACR_T], node: ast.AST) -> ACR_T:
        raise NotImplementedError

    # FIXME: this should run only on class creation, so metaclasses?
    def __attrs_post_init__(self):
        _fields = list(attr.fields_dict(type(self)).keys())
        # print(type(self), _fields)

        for name in self._attributes:
            _fields.remove(name)
        _fields.remove("_attributes")
        _fields.remove("_fields")

        self._fields = tuple(_fields)

        # _nonblock_fields = []
        # _block_fields = []

        # for name in self._fields:
        #     if isi


@attr.s(auto_attribs=True)
class Name(ACR):
    name: str
    is_symbol: bool = attr.ib(init=False, default=False)

    _attributes: Tuple[str, ...] = attr.ib(init=False, default=("is_symbol",))


CODE = Union[
    # stmt - from scope body
    ast.Delete, ast.Assign, ast.AugAssign, ast.AnnAssign,
    ast.Import, ast.ImportFrom,
    # Nonlocal, Global - we have symbol's scope for that
    # Expr - no need for it
    ast.Pass,  # so blocks only with pass will be fine
    ast.Break, ast.Continue,

    # expr - from breakdown of complex expressions
    ast.BoolOp, ast_NamedExpr, ast.BinOp, ast.UnaryOp,
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
    "ScopeReference"
]


CONTROL_FLOW = Union[  # TODO: not finished?
    "CodeBlock", "Block",

    # stmt - from scope body
    ast.Return, ast.Raise, ast.Assert,
    ast.Break, ast.Continue,

    # expr - from breakdown of complex expressions
    # ast.Yield, ast.YieldFrom for now it's in the CODE
]


# BlockContainer
# @attr.s(auto_attribs=True)
class FlowContainer(List[CONTROL_FLOW]):  # XXX: maybe ControlFlowSomething?
    def add_code(self, code: CODE) -> None:
        """Add code to latest block, if it's is not `CodeBlock`
        function will add new `CodeBlock` to `blocks` and add code there"""

        if len(self):
            block = self[-1]
            if type(block) is not CodeBlock:
                block = CodeBlock()
                self.append(block)
        else:
            block = CodeBlock()
            self.append(block)

        block.append(code)


# @attr.s(auto_attribs=True)
class CodeBlock(List[CODE]):
    """a.k.a. Basic block"""
    pass


# @attr.s(auto_attribs=True)
class Block(ACR):
    _block_fields: Tuple[str, ...] = ()

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        _fields = list(self._fields)
        _fields.remove("_block_fields")
        self._fields = tuple(_fields)


@attr.s(auto_attribs=True)
class BodyBlock(Block):
    body: FlowContainer = attr.ib(factory=FlowContainer, init=False)
    _block_fields: Tuple[str, ...] = attr.ib(init=False, default=("body",))


class ScopeType(Flag):  # XXX: maybe ScopeT?
    GLOBAL = auto()  # used with global keyword in this scope
    NONLOCAL = auto()  # used with nonlocal keyword in this scope
    LOCAL = auto()  # has an assertion in this scope
    # GLOBAL | NONLOCAL - not LOCAL
    # NONLOCAL | LOCAL - can it happen?
    # GLOBAL | LOCAL - can it happen?
    UNKNOWN = GLOBAL | NONLOCAL | LOCAL


@attr.s(auto_attribs=True)
class SymbolData(ACR):
    # it seems like symbol's scope doesn't change
    # throughout the scope execution
    scope: ScopeType = ScopeType.UNKNOWN

    imported: bool = False
    is_arg: bool = False

    type: PynalyserType = objectType

    # if we change from UNKNOWN to more specific it's fine
    # but if we change from specific to other specific than
    # probably something went wrong
    # is it the responsibility of this class to check this?
    def change_scope(self, new_scope: ScopeType, fail: bool = True) -> bool:
        if self.scope is ScopeType.UNKNOWN:
            self.scope = new_scope
            return True
        else:
            if not fail:
                return False

            # TODO: change to custom class
            raise ValueError(
                f"changing the `scope` from {self.scope} to {new_scope}")


class SymbolTable(DefaultDict[str, SymbolData]):
    def __init__(self, *args, **kwargs):
        super().__init__(SymbolData, *args, **kwargs)


@attr.s(auto_attribs=True)
class ScopeReference(ACR, ast.AST):  # so NodeTransformer could handle this
    """Refers to a single scope in the `scopes`
    of the local scope.
    """
    name: str
    id: int

    def get_scope(self, local_scope: "Scope") -> "Scope":
        return local_scope.scopes[self.name][self.id]


# do we need this class?
class ScopeDefs(Dict[int, "Scope"]):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(self, *args, **kwargs)
        self._last_index = 0

    def append(self, value: "Scope") -> None:
        self[self._last_index] = value
        self._last_index += 1

    @property
    def last_index(self) -> int:
        return self._last_index


@attr.s(auto_attribs=True)
class Scope(Name, BodyBlock):
    scopes: DefaultDict[str, ScopeDefs] = attr.ib(
        init=False, factory=lambda: defaultdict(ScopeDefs))
    symbol_table: SymbolTable = attr.ib(init=False, factory=SymbolTable)
    # parent? probably nay

    def add_scope(self, scope: "Scope") -> ScopeReference:
        defs = self.scopes[scope.name]
        reference = ScopeReference(scope.name, defs.last_index)
        defs.append(scope)
        return reference


# all of the inner scopes inside of the scope will be moved
# to the `scopes` and reference will take the place of the ast node
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
    # (it will generate lastest ast for earsier python versions)
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

    @classmethod
    def from_ast(cls: Type[ACR_T], node: ast.AST) -> ACR_T:
        assert type(node) is ast.ClassDef
        return cls(
            node.name, node.bases, node.keywords, node.decorator_list,
            lineno=node.lineno, col_offset=node.col_offset)


@attr.s(auto_attribs=True)
class Function(ScopeWithAttributes):
    # XXX: how to deal with the function returns?
    args: ast.arguments = attr.ib(factory=ast.arguments)
    # returns: Optional[ast.expr] = attr.ib(factory=ast.expr)  # is needed?
    decorator_list: List[ast.expr] = attr.ib(factory=list)

    is_symbol: bool = attr.ib(init=False, default=True)


LAMBDA_NAME = "<lambda>"


# lambdas and comprehensions will be moved to the `scopes`
# and reference will take the place of the ast node
@attr.s(auto_attribs=True)
class Lambda(ScopeWithAttributes):
    name: str = attr.ib(default=LAMBDA_NAME, init=False)
    args: ast.arguments = attr.ib(factory=ast.arguments)


@attr.s(auto_attribs=True)
class Comprehension(ScopeWithAttributes):
    # XXX: shouldn't have `body` from Scope,
    # but removing this will bring currently unneeded refactoring
    generators: List[ast.comprehension] = attr.ib(kw_only=True)


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
    pattern: ast_pattern
    guard: Optional[ast.expr]


@attr.s(auto_attribs=True)
class Match(ACRWithAttributes, Block):
    subject: ast.expr
    cases: List[MatchCase] = attr.ib(init=False, factory=list)
    _block_fields: Tuple[str, ...] = attr.ib(init=False, default=("cases",))


@attr.s(auto_attribs=True)
class With(ACRWithAttributes, BodyBlock):
    items: List[ast.withitem]


# python don't give us this info as attrs of the 'oresle'
# it's just a list of the 'stmt', but if we want,
# we can try to get this info from attrs of those 'stms's
# the problem is that if we will remove pass-es
# sometimes info will be lost, but now it's not needed so,
# I'll left it like that


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


class Loop(ACRWithAttributes, BodyElseBlock):  # XXX: do we need this class?
    pass


@attr.s(auto_attribs=True)
class For(Loop):
    target: ast.expr  # ? Union[ast.Name, ast.Tuple, ast.List]
    iter: ast.expr


@attr.s(auto_attribs=True)
class While(Loop):
    test: ast.expr


# async?? - Async class + inhertance
"""
def f(a):
    print(a)  # ???
"""

# class list
# def mark(index) -> id
# marked item's index will be tracked
# def get_index(id) -> index
