import io
import os

from . import portable_ast as ast
from .acr import Module, translate_ast_to_acr
from .analysers.pipeline import PIPELINE_FACTORY, create_pipeline, run_pipeline
from .analysers.tools import AnalysisContext
from .normalize_ast import normalize_ast_module


def parse(path: str) -> Module:
    return parse_open(path, "r", encoding="utf-8")


def parse_open(*args, **kwargs) -> Module:
    with open(*args, **kwargs) as stream:
        assert isinstance(stream, io.TextIOBase)
        return parse_stream(stream)  # type: ignore


def parse_stream(stream: io.TextIOWrapper) -> Module:
    with stream:
        return parse_ast(
            os.path.splitext(os.path.basename(stream.name))[0],
            ast.parse(stream.read()))


def parse_ast(name: str, module: ast.Module) -> Module:
    return translate_ast_to_acr(normalize_ast_module(module), name)


def analyse_file(
    source: str, factory: PIPELINE_FACTORY = create_pipeline
) -> AnalysisContext:

    ctx = AnalysisContext([parse(source)])
    return run_pipeline(ctx, factory)
