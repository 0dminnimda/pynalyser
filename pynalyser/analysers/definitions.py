import sys
from typing import Any, List, Optional, Union

from .. import acr, ast
from ..symbol import ScopeType
from ..types import Arg, Arguments, FunctionType, SymbolTableType
from .tools import Analyser, AnalysisContext, NameCollector


class SymTabAnalyser(Analyser, NameCollector):
    symtab: SymbolTableType

    def analyse(self, ctx: AnalysisContext) -> None:
        type_name = SymTabAnalyser.__name__
        if type_name in ctx.results:
            # TODO: use custom exception
            raise Exception(
                f"Key '{type_name}' is already in use"
                " for other AnalysisContext.results"
            )

        self.symtab = ctx.results[type_name] = SymbolTableType(name="WholeAnalysis")
        super().analyse(ctx)

    def visit(self, node: acr.NODE) -> Any:
        if isinstance(node, acr.Scope):
            prev = self.symtab
            # this symbol is used in self.scope + progress the definition
            self.symtab[node.name].next_def()
            try:
                return super().visit(node)
            finally:
                self.symtab = prev
        return super().visit(node)

    def handle_arg(self, name: str) -> Arg:
        symbol = self.symtab[name]
        symbol.is_arg = True

        if not symbol.change_scope(ScopeType.LOCAL, fail=False):
            raise SyntaxError(f"duplicate argument '{name}' in function definition")

        return Arg(name, symbol.current_symbol)

    def handle_function(self, scope: Union[acr.Lambda, acr.Function]) -> None:
        args = Arguments()
        symbol = self.symtab[scope.name]
        symbol.type = self.symtab = FunctionType(args)
        symbol.change_scope(ScopeType.LOCAL)
        symbol.holds_symbol_table = True

        if sys.version_info >= (3, 8):
            for arg in scope.args.posonlyargs:
                args.posargs.append(self.handle_arg(arg.arg))

        for arg in scope.args.args:
            args.args.append(self.handle_arg(arg.arg))

        for arg in scope.args.kwonlyargs:
            args.kwargs.append(self.handle_arg(arg.arg))

        if scope.args.vararg is not None:
            args.stararg = self.handle_arg(scope.args.vararg.arg)

        if scope.args.kwarg is not None:
            args.twostararg = self.handle_arg(scope.args.kwarg.arg)

    def handle_scope(self, node: acr.Scope) -> None:
        self.symtab[node.name].type = self.symtab = SymbolTableType(
            name=type(node).__name__
        )

    def visit_ListComp(self, node: acr.ListComp) -> None:
        self.handle_scope(node)

    def visit_SetComp(self, node: acr.SetComp) -> None:
        self.handle_scope(node)

    def visit_GeneratorExp(self, node: acr.GeneratorExp) -> None:
        self.handle_scope(node)

    def visit_DictComp(self, node: acr.DictComp) -> None:
        self.handle_scope(node)

    def visit_Lambda(self, node: acr.Lambda) -> None:
        self.handle_function(node)

    def visit_Function(self, node: acr.Function) -> None:
        self.handle_function(node)

    def visit_Class(self, node: acr.Class) -> None:
        self.handle_scope(node)

    def visit_Module(self, node: acr.Module) -> None:
        self.handle_scope(node)


_name_collector: NameCollector = NameCollector()


def progress_symbol_defs(symtab: SymbolTableType, node: acr.NODE) -> None:
    names: List[str] = []
    only_on_undef = False

    if isinstance(node, (acr.For, ast.AugAssign, ast.AnnAssign, ast.NamedExpr)):
        names.extend(_name_collector.collect_names(node.target))
    elif isinstance(node, ast.Assign):
        for sub_node in node.targets:
            names.extend(_name_collector.collect_names(sub_node))
    elif isinstance(node, (ast.Import, ast.ImportFrom)):
        names.extend(alias.asname or alias.name for alias in node.names)
    elif isinstance(node, (ast.Global, ast.Nonlocal)):
        names.extend(node.names)
        only_on_undef = True
    elif isinstance(node, ast.Name):
        names.append(node.id)
        only_on_undef = True
    # Delete, With, Match
    # Try cleans up after "except e as x"

    for name in names:
        symbol = symtab[name]
        if only_on_undef and symbol.is_currently_defined:
            continue
        symbol.next_def()


class DefinitionAnalyser(Analyser):
    symtab: SymbolTableType
    record_defs: bool = False

    def __init__(self, record_defs: Optional[bool] = None) -> None:
        if record_defs is not None:
            self.record_defs = record_defs

    def analyse(self, ctx: AnalysisContext) -> None:
        type_name = SymTabAnalyser.__name__
        if type_name not in ctx.results:
            # XXX: use custom exception?
            raise KeyError(f"Key '{type_name}' is required by {type(self).__name__}")

        self.symtab = ctx.results[type_name]
        super().analyse(ctx)

    def visit(self, node: acr.NODE) -> Any:
        if isinstance(node, acr.Scope):
            symbol = self.symtab[node.name]
            symbol.next_def()

            symtab = symbol.type
            assert isinstance(symtab, SymbolTableType)

            for symbol in symtab.values():
                symbol.reset()

            prev = self.symtab
            self.symtab = symtab

            try:
                return super().visit(node)
            finally:
                self.symtab = prev

        progress_symbol_defs(self.symtab, node)
        return super().visit(node)
