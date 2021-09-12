import ast
from collections import defaultdict
from typing import Any, DefaultDict, Dict, List, Optional, Set, TypeVar, Union

import attr


class ACR:
    """The base class for each class of
    abstract representation of the code.
    """
    pass

    # TODO: ? dump(indent=None)


@attr.s(auto_attribs=True)
class Name(ACR):  # or symbol?
    name: str


@attr.s(auto_attribs=True)
class Pointer(ACR):  # reference?
    action_ind: int
    # action  # TODO: how to point to action of the other variable


@attr.s(auto_attribs=True)
class Action(ACR):
    action: ast.AST  # TODO: stricter specification
    depends_on: Optional[Pointer] = None


class ActionOfBlock(Action):  # TODO: Action[Block]
    """inside variable, to refer to blocks, like if,
    indicates that in that block there are actions
    performed by the same name"""

    pass


@attr.s(auto_attribs=True)
class Actor(ACR):
    actions: List[Action] = attr.ib(factory=list, kw_only=True)


# XXX
# Block / Scope actions are mostly
# other blocks or keywords like return
# while Variable actions are keywords like global
# and all other (from Block / Scope) statements, expressions ...

@attr.s(auto_attribs=True)
class Variable(Name, Actor):
    scope: str = ""
    # initialised_from_args i.e. func parameter


@attr.s(auto_attribs=True)
class ActionSpace(Actor):
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
    # parent?


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
