import ast
import io
import os
from typing import List, Optional

from .acr.classes import Module
from .acr.translation import translate_ast_to_acr
from .analysis.types import TypeInference
from .analysis.scope import ScopeAnalyser
from .analysis.tools import Analyser, AnalysisContext
from .normalize_ast import normalize_ast_module


def parse(path: str) -> Module:
    return parse_open(path, "r", encoding="utf-8")


def parse_open(*args, **kwargs) -> Module:
    with open(*args, **kwargs) as stream:
        assert isinstance(stream, io.TextIOBase)
        return parse_stream(stream)


def parse_stream(stream: io.TextIOWrapper) -> Module:
    with stream:
        return parse_ast(
            os.path.splitext(os.path.basename(stream.name))[0],
            ast.parse(stream.read()))


def parse_ast(name: str, module: ast.Module) -> Module:
    return translate_ast_to_acr(normalize_ast_module(module), name)


def analyse_context(analysers: List[Analyser], ctx: AnalysisContext) -> None:
    for analyser in analysers:
        analyser.analyse(ctx)

DEFAULT_ANALYSERS = [
    ScopeAnalyser(),
    TypeInference(),
]


def analyse(ctx: AnalysisContext,
            analysers: Optional[List[Analyser]] = None) -> AnalysisContext:

    if analysers is None:
        analysers = DEFAULT_ANALYSERS
    assert analysers is not None  # for typechecker

    analyse_context(analysers, ctx)

    return ctx


def analyse_file(source: str,
                 analysers: Optional[List[Analyser]] = None) -> AnalysisContext:

    ctx = AnalysisContext([parse(source)])

    return analyse(ctx, analysers)
