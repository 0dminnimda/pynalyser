# XXX: this is also structure type, maybe merge?

from typing import TYPE_CHECKING, DefaultDict, Iterable, List, Optional

import attr

from .base_types import PynalyserType, DataType, UnknownType

if TYPE_CHECKING:
    from ..symbol import MultiDefSymbol, Symbol


@attr.s(auto_attribs=True, hash=True, cmp=False)
class SymbolTableType(DefaultDict[str, "MultiDefSymbol"], DataType):
    is_builtin: bool = attr.ib(default=True, init=False)

    def __attrs_pre_init__(self):
        from ..symbol import MultiDefSymbol

        super().__init__(MultiDefSymbol)  # for defaultdict

    def reset(self) -> None:
        for symbol in self.values():
            symbol.reset()


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

    def iter(self) -> Iterable[Arg]:
        yield from self.posargs
        yield from self.args
        if self.stararg is not None:
            yield self.stararg
        yield from self.kwargs
        if self.twostararg is not None:
            yield self.twostararg


@attr.s(auto_attribs=True, hash=True, cmp=False)
class FunctionType(SymbolTableType):
    args: Arguments
    return_type: PynalyserType = UnknownType

    name: str = attr.ib(default="function", init=False)

    def reset(self) -> None:
        super().reset()

        for arg in self.args.iter():
            self[arg.name].next_def()
