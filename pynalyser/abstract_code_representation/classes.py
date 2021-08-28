from typing import List, Set, Union, Any, TypeVar
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


class NameSpace(Set[NameT], ACR):
    def __getitem__(self, key: str) -> NameT:
        # for set str is the same as Name
        # because of __eq__ and __hash__
        result: Set[NameT] = {key} & self  # type: ignore

        # if len (result) == 0, then it ignores the loop,
        # otherwise return one only possible element
        for i in result:
            return i

        raise KeyError(key)


Action = Union[ast.AST, ACR]


class Actor(ACR):  # need separate class??
    def __init__(self, actions: List[Action] = []) -> None:
        self.actions = actions


class NamedActor(Name, Actor):
    def __init__(self, name: str, actions: List[Action] = []) -> None:
        Name.__init__(self, name)
        Actor.__init__(self, actions)


class Variable(NamedActor):
    def __init__(self, name: str, actions: List[Action] = [],
                 scope: str = "") -> None:
        self.scope = scope


class Scope(NamedActor):  # NamedScope
    def __init__(self, name: str,
                 actions: List[Action] = [],
                 actors: NameSpace[NamedActor] = NameSpace(),
                 scopes: NameSpace["Scope"] = NameSpace()) -> None:
        super().__init__(name, actions)
        self.actors = actors  # variables ???
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
    args: ast.arguments
    returns: ast.expr
    decorator_list: List[ast.AST]
    # body in in the actions of Actor

    # type_comment ? (i think no)


class Lambda(Function):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__("<lambda>", *args, **kwargs)


class Class(Scope):
    bases: List[ast.AST]  # parent-classes
    keywords: List[ast.keyword]  # metaclass and kws for it
    decorator_list: List[ast.AST]
    # body and members in in the actions of Actor
