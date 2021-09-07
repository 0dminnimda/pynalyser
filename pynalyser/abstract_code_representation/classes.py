from typing import List, Set, Union, Any, TypeVar, Dict, DefaultDict, Optional
from collections import defaultdict
import ast


class ACR:
    """The base class for each class of
    abstract representation of the code.
    """
    pass


class Name(ACR):
    def __init__(self, name: str) -> None:
        self.name = name

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: Any) -> bool:
        return self.name == other


NameT = TypeVar("NameT", bound=Name)


# def __getitem__(self, key: Union[str, NameT]) -> NameT:
#     if isinstance(key, Name):
#         key = key.name

#     super().__getitem__(key)


# class NameSpace(Dict[str, NameT], ACR):
    


# class NameSpace(Set[NameT], ACR):
#     def __getitem__(self, key: str) -> NameT:
#         # for set str is the same as Name
#         # because of __eq__ and __hash__
#         result: Set[NameT] = {key} & self  # type: ignore

#         # if len (result) == 0, then it ignores the loop,
#         # otherwise return one only possible element
#         for i in result:
#             return i

#         raise KeyError(key)

#     def add_redefinition(self, item: NameT) -> None:
#         if item in self:
#             self[item].


Action = Union[ast.AST, ACR]  # TODO: stricter specification


class Actor(ACR):
    def __init__(self, actions: List[Action] = []) -> None:
        self.actions = actions


class NamedActor(Name, Actor):
    def __init__(self, name: str, actions: List[Action] = []) -> None:
        Name.__init__(self, name)
        Actor.__init__(self, actions)


class Variable(NamedActor):
    def __init__(self, name: str,
                 actions: List[Action] = [],
                 scope: str = "") -> None:
        super().__init__(name, actions)
        self.scope = scope


Scopes = DefaultDict[str, Dict[int, "Scope"]]


# NamedScope
class Scope(NamedActor):
    def __init__(self,
                 name: str,
                 actions: List[Action] = [],
                 variables: Dict[str, Variable] = dict(),
                 scopes: Scopes = defaultdict(dict)
                 ) -> None:
        super().__init__(name, actions)
        self.variables = variables
        self.scopes = scopes  # definitions for classes and functions

    # action_space: NameSpace[NamedActor] = NameSpace(),
    #              scopes: NameSpace[Scope] = NameSpace(),
    # def __init__(self, name: str, *args, **kwargs) -> None:
    #     Name.__init__(self, name)
    #     Scope.__init__(self, *args, **kwargs)


class Module(Scope):
    """`name` is the name of the file that this module belongs to
    """
    pass


class Function(Scope):
    def __init__(self,
                 name: str,
                 actions: List[Action] = [],
                 variables: Dict[str, Variable] = dict(),
                 scopes: Scopes = defaultdict(dict),
                 args: ast.arguments = ast.arguments(),
                 returns: ast.expr = ast.expr(),
                 decorator_list: List[ast.AST] = [],
                 ) -> None:
        super().__init__(name, actions, variables, scopes)
        self.args = args
        self.returns = returns
        self.decorator_list = decorator_list
        # body in in the actions of Actor


# we will be trapped because
# lambda can be defined in every expression
# therefore any expression have it's out scope ? .. no? 
class Lambda(Function):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__("<lambda>", *args, **kwargs)


class Class(Scope):
    def __init__(self,
                 name: str,
                 actions: List[Action] = [],
                 variables: Dict[str, Variable] = dict(),
                 scopes: Scopes = defaultdict(dict),
                 bases: List[ast.AST] = [],  # parent-classes
                 metaclass: Optional[type] = None,
                 keywords: List[ast.keyword] = [],  # metaclass and kws for it
                 decorator_list: List[ast.AST] = []
                 ) -> None:
        super().__init__(name, actions, variables, scopes)
        self.bases = bases
        self.metaclass = metaclass
        self.keywords = keywords
        self.decorator_list = decorator_list
        # body and members in in the actions of Actor


# class Comprehension(Scope):
#     actions: List[ast.comprehension]  # generators


# class EltComprehension(Comprehension):
#     elt: ast.expr


# class ListComp(EltComprehension):
#     name = "<listcomp>"


# class SetComp(EltComprehension):
#     name = "<setcomp>"


# class GeneratorExp(EltComprehension):
#     name = "<genexpr>"


# class DictComp(Comprehension):
#     key: ast.expr
#     value: ast.expr
#     name = "<dictcomp>"


class BlockVariable(NamedActor):  # is there a need? why not Variable?
    """Just to be different from NamedActor"""


class Block(Actor):
    variables: Dict[str, BlockVariable]


class MatchCase(Block):
    pattern: ast.AST  # ast.pattern
    guard: Optional[ast.expr]


class Match(Block):
    actions: List[Action] = []
    # actions: List[MatchCase]  # XXX
    cases: List[MatchCase]


class With(Block):
    items: List[ast.withitem]


class Else(Block):
    pass


class BlockWIthElse(Block):
    orelse: Else


class If(BlockWIthElse):
    test: ast.expr


class ExceptHandler(Block):
    type: Optional[ast.expr] = None
    name: str


class Final(Block):
    pass


class Try(BlockWIthElse):
    handlers: List[ExceptHandler]
    finalbody: Final


class Loop(BlockWIthElse):
    pass


class For(Loop):
    target: Union[ast.Name, ast.Tuple, ast.List]
    iter: ast.expr


class While(Loop):
    test: ast.expr



# async?? - Async class + inhertance

"""
def f(a):
    print(a)  # ???
"""

# how to point to action of the other variable
