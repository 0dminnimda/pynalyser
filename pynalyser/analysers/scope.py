from typing import List
from .. import acr, ast
from ..symbol import ScopeType
from .definitions import DefinitionAnalyser
from .tools import NameCollector


_name_collector: NameCollector = NameCollector()


class ScopeAnalyser(DefinitionAnalyser):
    def setup_symbols_by_assign(self, *targets: ast.AST) -> None:
        names = []
        for sub_node in targets:
            names.extend(_name_collector.collect_names(sub_node))

        for name in names:
            symbol_data = self.symtab[name]

            # in the other case it's already defined
            symbol_data.change_scope(ScopeType.LOCAL)
            symbol_data.imported = False

    def visit_For(self, node: acr.For) -> None:
        self.setup_symbols_by_assign(node.target)

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
        names = _name_collector.collect_names(node.target)
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
