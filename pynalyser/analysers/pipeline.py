from typing import Callable, List, Type

from .redefinitions import RedefinitionAnalyser
from .scope import ScopeAnalyser
from .tools import Analyser, AnalysisContext
from .type_inference import TypeInference


PIPELINE = List[Analyser]
PIPE_FACTORY = Callable[[], PIPELINE]


def default_pipe() -> PIPELINE:
    return [
        ScopeAnalyser(),
        RedefinitionAnalyser(),
        TypeInference(),
    ]


def insert_in_pipeline(pipeline: PIPELINE, to_be_inserted: Analyser,
                       mode: str, relative_to: Type[Analyser]):
    """
    Create a copy of the pipeline with a new analyzer inserted into
    the pipeline after or before an instance of the given class

    `pipeline = insert_into_pipeline(`
    `    pipeline, MyAnalyser(), "after", AnalyserInThePipeline)`

    `mode` can be `'before'` or `'after'`
    """

    if mode not in ("before", "after"):
        raise ValueError(
            "insert_in_pipeline() mode must be 'before' or 'after'")

    i = 0
    for i, analyser in enumerate(pipeline):
        if isinstance(analyser, relative_to):
            break

    if mode == "after":
        i += 1

    return pipeline[:i] + [to_be_inserted] + pipeline[i:]


def run_pipeline(ctx: AnalysisContext,
                 factory: PIPE_FACTORY) -> AnalysisContext:

    for analyser in factory():
        analyser.analyse(ctx)

    return ctx
