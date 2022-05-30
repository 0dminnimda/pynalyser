import os
from typing import Iterable, List

from . import portable_ast as ast
from .acr import Module, translate_ast_to_acr
from .analysers.pipeline import PIPE_FACTORY, create_pipeline, run_pipeline
from .analysers.tools import AnalysisContext
from .normalize_ast import normalize_ast_module


def parse_file(path: str) -> Module:
    with open(path, mode="r", encoding='utf-8') as file:
        return parse_string(
            os.path.splitext(os.path.basename(file.name))[0],
            file.read())


def parse_string(filename: str, string: str) -> Module:
    return parse_ast(filename, ast.parse(string))


def parse_ast(filename: str, module: ast.Module) -> Module:
    return translate_ast_to_acr(normalize_ast_module(module), filename)


def analyse_files(
    paths: Iterable[str], factory: PIPE_FACTORY = create_pipeline
) -> AnalysisContext:

    return analyse_modules([parse_file(p) for p in paths], factory)


def analyse_modules(
    modules: List[Module], factory: PIPE_FACTORY = create_pipeline
) -> AnalysisContext:

    return run_pipeline(AnalysisContext(modules), factory)
