from typing import List, Optional
from ._types import PynalyserType, UnknownType
from .symbols import SymbolData

import attr


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
class FunctionType(PynalyserType):
    args: Arguments
    return_type: PynalyserType = UnknownType
