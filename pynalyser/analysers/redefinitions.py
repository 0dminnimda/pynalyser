from typing import Any, List

from .. import acr, ast
from ..types import SymbolTableType
from .scope import SymTabAnalyser
from .tools import Analyser, NameCollector


class RedefinitionAnalyser(SymTabAnalyser):
    symtab: SymbolTableType

    _name_collector: NameCollector = NameCollector()

    def visit(self, node: acr.NODE) -> Any:
        names: List[str] = []
        if isinstance(node, acr.Scope) and not isinstance(node, acr.Module):
            names.append(node.name)
        elif isinstance(node, (acr.For, ast.AugAssign, ast.NamedExpr)):
            names.extend(self._name_collector.collect_names(node.target))
        elif isinstance(node, ast.Assign):
            for sub_node in node.targets:
                names.extend(self._name_collector.collect_names(sub_node))
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names.extend(alias.asname or alias.name for alias in node.names)
        # Delete, With, Match
        # Try cleans up after "except e as x"

        for name in names:
            self.symtab[name].next_def()

        return super().visit(node)
