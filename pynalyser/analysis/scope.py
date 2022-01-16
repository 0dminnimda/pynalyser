import ast
from typing import List, Union

from ..acr import classes as acr_c
from .symbols import ScopeType
from .tools import Analyser


class AssignVisitor(ast.NodeVisitor):
    # accounted for:
    # Attribute - don't visit fields, XXX: for now
    # Subscript - don't visit fields
    # Starred - just visit itself
    # Name - add name, if we got here
    # List - just visit itself
    # Tuple - just visit itself
    # other nodes AFAIK will not appear here

    names: List[str] = []

    def get_names(self, node: ast.AST) -> List[str]:
        self.names.clear()
        self.visit(node)
        return self.names

    def visit_Attribute(self, node: ast.Attribute) -> None:
        pass

    def visit_Subscript(self, node: ast.Subscript) -> None:
        pass

    def visit_Name(self, node: ast.Name) -> None:
        self.names.append(node.id)


class ScopeAnalyser(Analyser):
    # we receive acr with global and nonlocal keywords
    # already transformed into symbol's scope value
    # but everything else is unknown and have to be filled here

    assign_visitor: AssignVisitor = AssignVisitor()

    def handle_scope(self, scope: acr_c.Scope) -> None:
        if scope.is_symbol:
            # this symbol is used in self.scope
            self.scope.symbol_table[scope.name]

    def handle_arguments(
        self, scope: Union[acr_c.Lambda, acr_c.Function]
    ) -> None:

        all_args: List[ast.arg] = (
            scope.args.posonlyargs + scope.args.args + scope.args.kwonlyargs)
        if scope.args.vararg:
            all_args.append(scope.args.vararg)
        if scope.args.kwarg:
            all_args.append(scope.args.kwarg)

        assert len(scope.symbol_table) == 0

        for arg in all_args:
            symb = scope.symbol_table[arg.arg]
            symb.is_arg = True
            if not symb.change_scope(ScopeType.LOCAL, fail=False):
                raise SyntaxError(
                    f"duplicate argument '{arg.arg}' in function definition")

    def visit_For(self, node: acr_c.For) -> None:
        self.setup_symbols_by_assign(node.target)

    def visit_Lambda(self, node: acr_c.Lambda) -> None:
        self.handle_arguments(node)
        self.handle_scope(node)

    def visit_ListComp(self, node: acr_c.ListComp) -> None:
        self.handle_scope(node)

    def visit_SetComp(self, node: acr_c.SetComp) -> None:
        self.handle_scope(node)

    def visit_GeneratorExp(self, node: acr_c.GeneratorExp) -> None:
        self.handle_scope(node)

    def visit_DictComp(self, node: acr_c.DictComp) -> None:
        self.handle_scope(node)

    def visit_Function(self, node: acr_c.Function) -> None:
        self.handle_arguments(node)
        self.handle_scope(node)

    def visit_Class(self, node: acr_c.Class) -> None:
        self.handle_scope(node)

    def setup_symbols_by_assign(self, *targets: ast.AST) -> None:
        names = []
        for sub_node in targets:
            names.extend(self.assign_visitor.get_names(sub_node))

        for name in names:
            symbol_data = self.scope.symbol_table[name]

            # in the other case it's already defined
            symbol_data.change_scope(ScopeType.LOCAL, fail=False)
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
            symbol_data = self.scope.symbol_table[name]
            symbol_data.imported = True

    def visit_Import(self, node: ast.Import) -> None:
        self.setup_symbols_by_import(node.names)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.setup_symbols_by_import(node.names)

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        names = self.assign_visitor.get_names(node.target)
        assert len(names) == 1
        name, = names

        symbol = self.scope.symbol_table[name]
        if isinstance(self.scope, acr_c.Comprehension):
            # in the other case it's already defined
            if not symbol.change_scope(ScopeType.NONLOCAL, fail=False):
                raise NotImplementedError(
                    "NamedExpr should make symbol local for enclosing scope")
        else:
            # in the other case it's already defined
            symbol.change_scope(ScopeType.LOCAL, fail=False)

        symbol.imported = False

    def visit_Name(self, node: ast.Name) -> None:
        # this name have been used in this scope
        self.scope.symbol_table[node.id]
