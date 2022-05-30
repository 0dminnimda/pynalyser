from enum import Flag, auto
from typing import Any, List

import attr

from .types import PynalyserType, UnknownType


# XXX: maybe ScopeKind?
class ScopeType(Flag):
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


class MultiDefSymbol:
    _symbols: List[Symbol]
    _i: int

    def __init__(self) -> None:
        self._symbols = [Symbol()]
        self.reset()

    @property
    def current_symbol(self) -> Symbol:
        return self._symbols[self._i]

    def next_def(self) -> None:
        self._i += 1
        if len(self._symbols) == self._i:
            self._symbols.append(Symbol())

    def reset(self):
        self._i = 0

    scope: ScopeType

    imported: bool
    is_arg: bool
    holds_symbol_table: bool

    type: PynalyserType

    def change_scope(self, new_scope: ScopeType, fail: bool = True) -> bool:
        return self.current_symbol.change_scope(new_scope, fail)

    _names = "scope", "imported", "is_arg", "holds_symbol_table", "type"

    def __getattr__(self, name: str) -> Any:
        # return getattr(self.current_symbol, name)
        if name in self._names:
            return getattr(self.current_symbol, name)
        super().__getattribute__(name)  # no return

    def __setattr__(self, name: str, value: Any) -> None:
        if name in self._names:
            return setattr(self.current_symbol, name, value)
        super().__setattr__(name, value)
