import ast
from collections import defaultdict
from typing import (
    Any, DefaultDict, Dict, List, Optional, Set, TypeVar, Union, Generic)

import attr


class ACR:
    """The base class for each class of
    abstract representation of the code.
    """
    pass

    # TODO: abc ? dump(indent=None), from_ast, to_ast


@attr.s(auto_attribs=True)
class Name(ACR):
    name: str


@attr.s(auto_attribs=True)
class Pointer(ACR):  # reference?
    action_ind: int
    # action  # TODO: how to point to action of the other variable


T = TypeVar("T")


@attr.s(auto_attribs=True)
class Action(ACR, Generic[T]):
    action: T
    depends_on: Optional[Pointer] = None


class ActionOfBlock(Action["Block"]):
    """inside variable, to refer to blocks, like if,
    indicates that in that block there are actions
    performed by the same name"""

    pass


@attr.s(auto_attribs=True)
class Actor(ACR, Generic[T]):
    actions: List[Action[T]] = attr.ib(factory=list, kw_only=True)


# XXX
# Block / Scope actions are mostly
# other blocks or keywords like return
# while Variable actions are keywords like global
# and all other (from Block / Scope) statements, expressions ...

# Import? ImportFrom?
# imports will create new names / override existing ones
# (single or several ones!) case with several ones is the problem
# they also should be threated as a kind of function call,
# because they execute the module's code upon import
# and we also can monkey patch data inside those modules,
# to effectively change the bahaviour of the imported module
variable_actions = Union[
    # stmt - from scope body
    ast.Delete, ast.Assign, ast.AugAssign, ast.AnnAssign,
    # import will be splitted to initialize each name separately
    # Import(original_name) # asname - variable names
    # ImportFrom(module, original_name, level)
    ast.Global, ast.Nonlocal, ast.Expr,

    # expr - from breakdown of complex expressions
    ast.BoolOp, ast.NamedExpr, ast.BinOp, ast.UnaryOp,
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

    # XXX: Pointer?

    # block should include Constant, but variable actions shouldn't
]

# Pass probably just shouldn't be included anywhere at all
# python will check the correctness of the syntax,
# we don't care about that

action_space_actions = [
    # stmt - from scope body
    ast.Return, ast.Raise, ast.Assert,
    ast.Break, ast.Continue,

    # expr - from breakdown of complex expressions
    ast.Yield, ast.YieldFrom
]


@attr.s(auto_attribs=True)
class Variable(Name, Actor[variable_actions]):  # or symbol?
    scope: str = ""
    # TODO: initialised_from_args i.e. func parameter
    # imported? ...


@attr.s(auto_attribs=True)
class ActionSpace(Actor[ast.AST]):  # TODO: make T specification correct
    """just to distinguish between Block and Scope,
    those are different things
    that are used in the different context"""

    variables: Dict[str, Variable] = attr.ib(factory=dict, kw_only=True)
    scopes: DefaultDict[str, Dict[int, "Scope"]] = attr.ib(
        factory=lambda: defaultdict(dict), kw_only=True)


@attr.s(auto_attribs=True)
class Block(ActionSpace):
    pass


@attr.s(auto_attribs=True)
class Scope(Name, ActionSpace):
    pass
    # parent? probably nay


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
    # body and members in in the actions of Actor


@attr.s(auto_attribs=True)
class Function(Scope):
    args: ast.arguments = attr.ib(factory=ast.arguments)
    # returns: ast.expr = attr.ib(factory=ast.expr)  # is needed?
    decorator_list: List[ast.AST] = attr.ib(factory=list)
    # body in in the actions of Actor


# lambdas and comprehensions will be moved to the scopes
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
class MatchCase(Block):
    pattern: ast.AST  # ast.pattern  # XXX: 3.10+
    guard: Optional[ast.expr]


@attr.s(auto_attribs=True)
class Match(Block):
    cases: List[MatchCase] = attr.ib(factory=list)
    # actions: List[MatchCase]  # XXX


@attr.s(auto_attribs=True)
class With(Block):
    items: List[ast.withitem]


class Else(Block):
    pass


@attr.s(auto_attribs=True)
class BlockWIthElse(Block):
    orelse: Else


@attr.s(auto_attribs=True)
class If(BlockWIthElse):
    test: ast.expr


@attr.s(auto_attribs=True)
class ExceptHandler(Block):
    type: Optional[ast.expr] = None
    name: Optional[str] = None


class Final(Block):
    pass


@attr.s(auto_attribs=True)
class Try(BlockWIthElse):
    handlers: List[ExceptHandler]
    finalbody: Final


class Loop(BlockWIthElse):
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
