from typing import List, Set, Union, Any
import ast


class ACR:
    """The base class for each class of
    abstract representation of the code.
    """
    pass


Action = Union[ast.AST, ACR]


class Actor(ACR):
    def __init__(self, *acts: Action) -> None:
        self.acts = list(acts)


class Name(Actor):
    def __init__(self, name: str, *acts: Action) -> None:
        super().__init__(*acts)
        self.name = name

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: Any) -> bool:
        return self.name == other


class ActionSpace(ACR, Set[Name]):
    def __getitem__(self, key: str) -> Name:
        # for set str is the same as Name
        # because of __eq__ and __hash__
        result: Set[Name] = {key}.intersection(self)  # type: ignore

        # if len (result) == 0, then it ignores the loop,
        # otherwise return the only possible element
        for i in result:
            return i

        raise KeyError(key)


class Scope(Actor):
    def __init__(self, scope: ActionSpace, *acts: Action) -> None:
        super().__init__(*acts)
        self.scope = scope


class Module(Scope):
    pass
    # filename ?


class Function(Scope):
    pass


class Class(Scope):
    pass

