from typing import DefaultDict, List, Optional

import attr

from ._types import PynalyserType, UnknownType
from .symbol import SymbolData


@attr.s(auto_attribs=True, hash=True)
class SymbolTableType(DefaultDict[str, SymbolData], PynalyserType):
    def __attrs_pre_init__(self):
        super().__init__()  # for DefaultDict


@attr.s(auto_attribs=True, hash=True)
class Arg:
    name: str
    symbol: SymbolData
    default: Optional[PynalyserType] = None


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
