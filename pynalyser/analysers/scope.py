import sys
from typing import Any, List, Union

from .. import acr, ast
from ..symbol import ScopeType
from ..types import Arg, Arguments, FunctionType, SymbolTableType
from .tools import Analyser, AnalysisContext, NameCollector


# XXX: split into creation of symtab and symbols
class ScopeAnalyser(Analyser, NameCollector):
    symtab: SymbolTableType

    def analyse(self, ctx: AnalysisContext) -> None:
        if type(self).__name__ in ctx.results:
            # TODO: use custom exception
            raise Exception(
                f"Key '{type(self).__name__}' is already in use"
                " for other AnalysisContext.results"
            )

        self.symtab = ctx.results[type(self).__name__] = SymbolTableType()
        super().analyse(ctx)

    def visit(self, node: acr.NODE) -> Any:
        if isinstance(node, acr.Scope):
            prev = self.symtab
            if node.is_symbol:
                # this symbol is used in self.scope
                self.symtab[node.name]
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

    def visit_For(self, node: acr.For) -> None:
        self.setup_symbols_by_assign(node.target)

    def visit_ListComp(self, node: acr.ListComp) -> None:
        self.symtab[node.name].type = self.symtab = SymbolTableType()

    def visit_SetComp(self, node: acr.SetComp) -> None:
        self.symtab[node.name].type = self.symtab = SymbolTableType()

    def visit_GeneratorExp(self, node: acr.GeneratorExp) -> None:
        self.symtab[node.name].type = self.symtab = SymbolTableType()

    def visit_DictComp(self, node: acr.DictComp) -> None:
        self.symtab[node.name].type = self.symtab = SymbolTableType()

    def visit_Lambda(self, node: acr.Lambda) -> None:
        self.handle_function(node)

    def visit_Function(self, node: acr.Function) -> None:
        self.handle_function(node)

    def visit_Class(self, node: acr.Class) -> None:
        self.symtab[node.name].type = self.symtab = SymbolTableType()

    def visit_Module(self, node: acr.Module) -> None:
        self.symtab[node.name].type = self.symtab = SymbolTableType()

    def setup_symbols_by_assign(self, *targets: ast.AST) -> None:
        names = []
        for sub_node in targets:
            names.extend(self.collect_names(sub_node))

        for name in names:
            symbol_data = self.symtab[name]

            # in the other case it's already defined
            symbol_data.change_scope(ScopeType.LOCAL)
            symbol_data.imported = False

    def visit_Assign(self, node: ast.Assign) -> None:
        self.setup_symbols_by_assign(*node.targets)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        pass

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        # XXX: should be only one name in the end:
        self.setup_symbols_by_assign(node.target)

    def setup_symbols_by_import(self, targets: List[ast.alias]) -> None:
        for alias in targets:
            name = alias.asname or alias.name  # those are never == ""
            symbol_data = self.symtab[name]
            symbol_data.imported = True

    def visit_Import(self, node: ast.Import) -> None:
        self.setup_symbols_by_import(node.names)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.setup_symbols_by_import(node.names)

    def visit_Global(self, node: ast.Global) -> None:
        for name in node.names:
            symbol_data = self.symtab[name]
            # generally imports before global should not be allowed,
            # but cpython allows it https://tiny.one/global-in-docs
            symbol_data.change_scope(ScopeType.GLOBAL)

    def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
        for name in node.names:
            symbol_data = self.symtab[name]
            # generally imports before nonlocal should not be allowed,
            # but cpython allows it https://tiny.one/nonlocal-in-docs
            symbol_data.change_scope(ScopeType.NONLOCAL)

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        names = self.collect_names(node.target)
        assert len(names) == 1
        name, = names

        symbol = self.symtab[name]
        if isinstance(self.scope, acr.Comprehension):
            # in the other case it's already defined
            if not symbol.change_scope(ScopeType.NONLOCAL, fail=False):
                raise NotImplementedError(
                    "NamedExpr should make symbol local for enclosing scope"
                )
        else:
            # in the other case it's already defined
            symbol.change_scope(ScopeType.LOCAL)

        symbol.imported = False

    def visit_Name(self, node: ast.Name) -> None:
        # this name have been used in this scope
        self.symtab[node.id]


class SymTabAnalyser(Analyser):
    symtab: SymbolTableType

    def analyse(self, ctx: AnalysisContext) -> None:
        if ScopeAnalyser.__name__ not in ctx.results:
            # XXX: use custom exception?
            raise KeyError(
                f"Key '{ScopeAnalyser.__name__}' is"
                f" requeued by {type(self).__name__}"
            )

        self.symtab = ctx.results[ScopeAnalyser.__name__]
        super().analyse(ctx)

    def visit(self, node: acr.NODE) -> Any:
        if isinstance(node, acr.Scope):
            prev = self.symtab
            symtab = self.symtab[node.name].type
            assert isinstance(symtab, SymbolTableType)
            self.symtab = symtab

            for symbol in symtab.values():
                symbol.reset()

            try:
                return super().visit(node)
            finally:
                self.symtab = prev

        return super().visit(node)
