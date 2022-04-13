from typing import Callable, List, Type

from .scope import ScopeAnalyser
from .tools import Analyser, AnalysisContext
from .type_inference import TypeInference


PIPELINE = List[Analyser]
PIPELINE_FACTORY = Callable[[], PIPELINE]


def create_pipeline() -> PIPELINE:
    return [
        ScopeAnalyser(),
        TypeInference(),
    ]


def insert_in_pipeline(pipeline: PIPELINE, to_be_inserted: Analyser,
                       relative_to: Type[Analyser], before: bool = True):
    i = 0
    for i, analyser in enumerate(pipeline):
        if isinstance(analyser, relative_to):
            break

    if not before:
        i += 1

    return pipeline[:i] + [to_be_inserted] + pipeline[i:]


def run_pipeline(ctx: AnalysisContext,
                 factory: PIPELINE_FACTORY) -> AnalysisContext:

    for analyser in factory():
        analyser.analyse(ctx)

    return ctx
