from enum import Flag, auto
from typing import DefaultDict

import attr

from .types import PynalyserType, UnknownType


class ScopeType(Flag):  # XXX: maybe ScopeT?
    GLOBAL = auto()  # used with global keyword in this scope
    NONLOCAL = auto()  # used with nonlocal keyword in this scope
    LOCAL = auto()  # has an assertion in this scope
    # GLOBAL | NONLOCAL - not LOCAL
    # NONLOCAL | LOCAL - can it happen?
    # GLOBAL | LOCAL - can it happen?
    UNKNOWN = GLOBAL | NONLOCAL | LOCAL


# TODO: rename to Symbol and look at variables that use this class
@attr.s(auto_attribs=True)
class Symbol:
    # it seems like symbol's scope doesn't change
    # throughout the scope execution
    scope: ScopeType = ScopeType.UNKNOWN

    imported: bool = False  # TODO: handle this in acr translation
    is_arg: bool = False
    holds_symbol_table: bool = False

    type: PynalyserType = UnknownType

    # if we change from UNKNOWN to more specific it's fine
    # but if we change from specific to other specific than
    # probably something went wrong
    # is it the responsibility of this class to check this?
    def change_scope(self, new_scope: ScopeType, fail: bool = True) -> bool:
        # TODO: enable more options:
        # from unspecific to specific
        # GLOBAL | NONLOCAL, NONLOCAL | LOCAL, GLOBAL | LOCAL
        # is ok to go to
        # GLOBAL or NONLOCAL, NONLOCAL or LOCAL, GLOBAL or LOCAL
        if self.scope is ScopeType.UNKNOWN:
            self.scope = new_scope
            return True
        elif self.scope == new_scope:
            return True
        else:
            if not fail:
                return False

            # TODO: change to custom class
            raise ValueError(
                f"changing the `scope` from {self.scope} to {new_scope}")


class SymbolTable(DefaultDict[str, Symbol]):
    def __init__(self, *args, **kwargs):
        super().__init__(Symbol, *args, **kwargs)
