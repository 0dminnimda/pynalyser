from typing import Any, Dict, List

import attr

from ..acr import classes as acr_c
from ..acr.utils import NodeVisitor


@attr.s(auto_attribs=True)
class AnalysisContext:
    modules: List[acr_c.Module]
    results: Dict[str, Any] = attr.ib(init=False, factory=lambda: dict())


class Analyser(NodeVisitor):
    context: AnalysisContext

    def analyse(self, ctx: AnalysisContext) -> None:
        self.start(ctx.modules[0])
        self.context = ctx
