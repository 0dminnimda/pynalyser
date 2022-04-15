from typing import Any, Dict, List

import attr

from .. import acr


@attr.s(auto_attribs=True)
class AnalysisContext:
    modules: List[acr.Module]
    results: Dict[str, Any] = attr.ib(init=False, factory=lambda: dict())


class Analyser(acr.NodeVisitor):
    context: AnalysisContext

    def analyse(self, ctx: AnalysisContext) -> None:
        self.context = ctx
        self.start(ctx.modules[0])
