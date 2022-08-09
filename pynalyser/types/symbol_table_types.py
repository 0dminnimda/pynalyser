# XXX: this is also structure type, maybe merge?

from typing import TYPE_CHECKING, DefaultDict, List, Optional

import attr

from .base_types import PynalyserType, UnknownType

if TYPE_CHECKING:
    from ..symbol import Symbol, MultiDefSymbol


@attr.s(auto_attribs=True, hash=True)
class SymbolTableType(DefaultDict[str, "MultiDefSymbol"], PynalyserType):
    def __attrs_pre_init__(self):
        from ..symbol import MultiDefSymbol

        super().__init__(MultiDefSymbol)  # for defaultdict


@attr.s(auto_attribs=True, hash=True, auto_detect=True)
class Arg:
    name: str
    symbol: "Symbol"
    default: Optional[PynalyserType] = None

    def __repr__(self) -> str:
        default = "" if self.default is None else " = " + str(self.default)
        return f"<{self.name}: {self.symbol.type.as_str}{default}>"


@attr.s(auto_attribs=True, hash=True)
class Arguments:
    posargs: List[Arg] = attr.ib(factory=list)
    args: List[Arg] = attr.ib(factory=list)
    stararg: Optional[Arg] = None
    kwargs: List[Arg] = attr.ib(factory=list)
    twostararg: Optional[Arg] = None


@attr.s(auto_attribs=True, hash=True)
class FunctionType(SymbolTableType):
    args: Arguments
    return_type: PynalyserType = UnknownType
