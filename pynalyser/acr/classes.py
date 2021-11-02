import ast
import sys
from collections import defaultdict
from enum import Flag, auto
from typing import (
    Any, DefaultDict, Dict, Generic, List, Optional, Set, TypeVar, Union)

import attr

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


class ACR:
    """The base class for each class of
    abstract representation of the code.
    """
    pass

    # TODO: abc ? dump(indent=None), from_ast, to_ast


@attr.s(auto_attribs=True)
class Name(ACR):
    name: str


# Import? ImportFrom?
# imports will create new names / override existing ones
# (single or several ones!) case with several ones is the problem
# they also should be threated as a kind of function call,
# because they execute the module's code upon import
# and we also can monkey patch data inside those modules,
# to effectively change the bahaviour of the imported module
CODE = Union[  # TODO: not finished
    # stmt - from scope body
    ast.Delete, ast.Assign, ast.AugAssign, ast.AnnAssign,
    # import will be splitted to initialize each name separately
    # Import(original_name) # asname - variable names
    # ImportFrom(module, original_name, level)
    ast.Global, ast.Nonlocal, ast.Expr,

    # expr - from breakdown of complex expressions
    ast.BoolOp, ast_NamedExpr, ast.BinOp, ast.UnaryOp,
    ast.IfExp,  # ?
    ast.Dict, ast.Set, ast.Await,
    # XXX: YieldFrom don't affect object immediately ...
    ast.Compare, ast.Call, ast.FormattedValue,
    # XXX: why should we have just JoinedStr? it can have
    # several FormattedValue with different variables inside...
    # it should appear in context of the Assign, i guess
    ast.Attribute, ast.Subscript,
    ast.Starred,  # can act on 'a' only in situations like 'f(*a)'
    # other situations is in assigns,
    # and we don't care about possible previous state here,
    # because we're overriding it

    # Name is used in other nodes, but we don't
    # care about single name mention, it doesn't do anything
    ast.List, ast.Tuple,
    # Slice can appear only in Subscript,
    # and probably doesn't have any effect on the variables

    "ScopeReference"

    # block should include Constant, but variable actions shouldn't
]

# Pass probably just shouldn't be included anywhere at all
# python will check the correctness of the syntax,
# but we don't care about that

CONTROL_FLOW = Union[  # TODO: not finished
    "CodeBlock", "BlockContainer",

    # stmt - from scope body
    ast.Return, ast.Raise, ast.Assert,
    ast.Break, ast.Continue,

    # expr - from breakdown of complex expressions
    ast.Yield, ast.YieldFrom
]


# @attr.s(auto_attribs=True)
class FlowContainer(List[CONTROL_FLOW]):  # XXX: maybe ControlFlowSomething?
    pass


# @attr.s(auto_attribs=True)
class CodeBlock(List[CODE]):
    """a.k.a. Basic block"""
    pass


# @attr.s(auto_attribs=True)
class Block(ACR):
    pass


@attr.s(auto_attribs=True)
class BodyBlock(Block):
    body: FlowContainer = attr.ib(factory=FlowContainer, init=False)


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

    # if we change from UNKNOWN to more specific it's fine
    # but if we change from specific to other specific than
    # probably something went wrong
    # is it the responsibility of this class to check this?
    # XXX: change_scope(self, new_scope: ScopeType) -> None


class SymbolTable(DefaultDict[str, SymbolData]):
    pass


@attr.s(auto_attribs=True)
class ScopeReference(ACR):
    """Refers to a single scope in the `scopes`
    of the local scope.
    """
    name: str
    id: int

    def get_scope(self, local_scope: "Scope") -> "Scope":
        return local_scope.scopes[self.name][self.id]


# do we need this class?
class ScopeDefs(Dict[int, "Scope"], ACR):
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
        factory=lambda: defaultdict(ScopeDefs), init=False)
    symbol_table: SymbolTable = attr.ib(
        factory=SymbolTable, init=False)
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
    pass


@attr.s(auto_attribs=True)
class Class(Scope):
    bases: List[ast.AST] = attr.ib(factory=list)  # parent-classes
    metaclass: Optional[type] = None
    # initially metaclass and kws for it
    keywords: List[ast.keyword] = attr.ib(factory=list)
    decorator_list: List[ast.AST] = attr.ib(factory=list)


@attr.s(auto_attribs=True)
class Function(Scope):
    # XXX: how to deal with the function returns?
    args: ast.arguments = attr.ib(factory=ast.arguments)
    # returns: ast.expr = attr.ib(factory=ast.expr)  # is needed?
    decorator_list: List[ast.expr] = attr.ib(factory=list)


# lambdas and comprehensions will be moved to the `scopes`
# and reference will take the place of the ast node
@attr.s(auto_attribs=True)
class Lambda(Scope):
    name: str = attr.ib(default="<lambda>", init=False)
    args: ast.arguments = attr.ib(factory=ast.arguments)


@attr.s(auto_attribs=True)
class Comprehension(Scope):
    generators: List[ast.comprehension] = attr.ib(factory=list, kw_only=True)
    # actions: List[ast.comprehension]  # XXX


@attr.s(auto_attribs=True)
class EltComprehension(Comprehension):
    elt: ast.expr


@attr.s(auto_attribs=True)
class ListComp(EltComprehension):
    name: str = attr.ib(default="<listcomp>", init=False)


@attr.s(auto_attribs=True)
class SetComp(EltComprehension):
    name: str = attr.ib(default="<setcomp>", init=False)


@attr.s(auto_attribs=True)
class GeneratorExp(EltComprehension):
    name: str = attr.ib(default="<genexpr>", init=False)


@attr.s(auto_attribs=True)
class DictComp(Comprehension):
    key: ast.expr
    value: ast.expr
    name: str = attr.ib(default="<dictcomp>", init=False)


@attr.s(auto_attribs=True)
class MatchCase(BodyBlock):
    pattern: ast_pattern
    guard: Optional[ast.expr]


@attr.s(auto_attribs=True)
class Match(Block):
    cases: List[MatchCase] = attr.ib(factory=list)
    # actions: List[MatchCase]  # XXX


@attr.s(auto_attribs=True)
class With(BodyBlock):
    items: List[ast.withitem]


@attr.s(auto_attribs=True)
class BodyElseBlock(BodyBlock):
    orelse: FlowContainer = attr.ib(factory=FlowContainer, init=False)


@attr.s(auto_attribs=True)
class If(BodyElseBlock):
    test: ast.expr


@attr.s(auto_attribs=True)
class ExceptHandler(BodyBlock):
    type: Optional[ast.expr] = None
    name: Optional[str] = None


@attr.s(auto_attribs=True)
class Try(BodyElseBlock):
    handlers: List[ExceptHandler] = attr.ib(factory=list, init=False)
    finalbody: FlowContainer = attr.ib(factory=FlowContainer, init=False)


class Loop(BodyElseBlock):  # XXX: do we need this class?
    pass


@attr.s(auto_attribs=True)
class For(Loop):
    target: Union[ast.Name, ast.Tuple, ast.List]
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
