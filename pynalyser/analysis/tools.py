from typing import Any, Dict, List

import attr

from ..acr import classes as acr_c
from .. import acr
from ..acr.utils import NodeVisitor
from ..graph_visit_casher.ast_cacher import AstRecorder
from ..graph_visit_casher.cacher import Change, Reproducer


@attr.s(auto_attribs=True)
class AnalysisContext:
    modules: List[acr_c.Module]
    results: Dict[str, Any] = attr.ib(init=False, factory=lambda: dict())


class Analyser(NodeVisitor):
    context: AnalysisContext

    def analyse(self, ctx: AnalysisContext) -> None:
        self.context = ctx
        self.start(ctx.modules[0])


class _Analyser(AstRecorder):
    # context: AnalysisContext
    # relevant_records: List[str]
    _reproducers: List[Reproducer]
    # init_data: Dict[str, Any]

    def __init__(self) -> None:
        pass

    def cacher_visit(self) -> None:
        super().cacher_visit()
        for reproducer in self._reproducers:
            reproducer.visit()

    def analyse(self, ctx: AnalysisContext) -> None:
        data = dict(scope=ctx.modules[0], block=ctx.modules[0])
        relevant_records = self.prepare_for_analysis(ctx, data)
        self.reset(data)

        self._reproducers = []
        for name, record in ctx.results.items():
            if name in relevant_records:
                self._reproducers.append(Reproducer(data, record))

        # relevant_records = getattr(self, "relevant_records", None)
        # if relevant_records is None:
        #     raise AttributeError("'relevant_records' is not defined, "
        #                          "'prepare_for_analysis' requires it")
        #     # raise AttributeError(
        #     #     "'relevant_records' should be set in user-defined "
        #     #     "`prepare_for_analysis` that should use "
        #     #     "`Analyser.prepare_for_analysis`")

        # start analysis
        self.visit(ctx.modules[0])

        self.finish_analysis(ctx)
        ctx.results[type(self).__name__] = self.cacher.changes

    def prepare_for_analysis(
            self, ctx: AnalysisContext, data: Dict[str, Any]) -> List[str]:

        return []

    def finish_analysis(self, ctx: AnalysisContext) -> None:
        pass
