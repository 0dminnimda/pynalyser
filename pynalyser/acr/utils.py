import ast
from collections import defaultdict
from typing import (Any, Collection, Iterator, List, NamedTuple, Optional,
                    Tuple, Union)

from .classes import (ACR, Block, CodeBlock, FlowContainer, Module, Scope,
                      ScopeReference)

### Dumping


class Context(NamedTuple):
    annotate_fields: bool
    include_attributes: bool
    indent: Optional[str]


def dump(
        obj: Union[ACR, ast.AST], annotate_fields: bool = True,
        include_attributes: bool = False, *,
        indent: Optional[Union[str, int]] = None) -> str:
    if not isinstance(obj, (ACR, ast.AST, list, dict)):
        raise TypeError(  # XXX: should we force it?
            f"expected one of the AST / ACR / list / dict, "
            "got {type(obj).__name__}")
    if indent is not None and not isinstance(indent, str):
        indent = " " * indent
    return _format(
        obj, Context(annotate_fields, include_attributes, indent), lvl=0)[0]


def _format(obj: Any, ctx: Context, lvl: int) -> Tuple[str, bool]:
    if ctx.indent is not None:
        lvl += 1
        prefix = "\n" + ctx.indent * lvl
        sep = ",\n" + ctx.indent * lvl
    else:
        prefix = ""
        sep = ", "

    if isinstance(obj, list):
        args = []
        allsimple = True

        for item in obj:
            value, simple = _format(item, ctx, lvl)
            allsimple = allsimple and simple
            args.append(value)

        value, allsimple = _format_args_with_allsimple(
            prefix, sep, args, allsimple)

        value = f"[{value}]"
        if type(obj) is not list:
            value = f"{type(obj).__name__}({value})"
        return value, allsimple

    if isinstance(obj, dict):
        args = []
        allsimple = True

        for key, value in obj.items():
            # dict key should be "simple"
            value, simple = _format(value, ctx, lvl)
            allsimple = allsimple and simple
            args.append(f"{key!r}: {value}")

        value, allsimple = _format_args_with_allsimple(
            prefix, sep, args, allsimple)

        value = f"{{{value}}}"
        if isinstance(obj, defaultdict):
            value = f"{type(obj).__name__}({obj.default_factory}, {value})"
        elif type(obj) is not dict:
            value = f"{type(obj).__name__}({value})"

        return value, allsimple

    if isinstance(obj, (ACR, ast.AST)):
        value, allsimple = _format_args_with_allsimple(
            prefix, sep, *_format_ast_or_acr(obj, ctx, lvl))
        return f"{type(obj).__name__}({value})", allsimple

    return repr(obj), True


def _format_args_with_allsimple(prefix: str, sep: str, args: Collection[str],
                                allsimple: bool) -> Tuple[str, bool]:
    if allsimple and len(args) <= 3:
        return ", ".join(args), not args
    return prefix + sep.join(args), False


def _format_attr(inst: Any, name: str, ctx: Context,
                 lvl: int) -> Tuple[str, bool]:
    return _format(
        getattr(inst, name, "<Is not an attribute of the object>"), ctx, lvl)


def _format_ast_or_acr(obj: Union[ast.AST, ACR], ctx: Context,
                       lvl: int) -> Tuple[List[str], bool]:
    args = []
    allsimple = True

    for name in obj._fields:
        value, simple = _format_attr(obj, name, ctx, lvl)
        allsimple = allsimple and simple
        if ctx.annotate_fields:
            args.append(f"{name}={value}")
        else:
            args.append(value)

    if ctx.include_attributes and obj._attributes:
        for name in obj._attributes:
            value, simple = _format_attr(obj, name, ctx, lvl)
            allsimple = allsimple and simple
            args.append(f"{name}={value}")

    return args, allsimple


### Tree traversing


NODE = Union[ACR, ast.AST]


class NodeVisitor:
    _ast_visitor = ast.NodeVisitor

    scope: Scope
    block: Block
    # strict: bool = False
    # auto_global_visit: bool = True

    def start(self, init_scope_block: Scope,
              to_visit: Optional[NODE] = None) -> Any:

        self.scope = self.block = init_scope_block

        if to_visit is None:
            result = self.visit(init_scope_block)
        else:
            result = self.visit(to_visit)

        del self.scope, self.block
        return result

    def _acr_generic_visit(self, node: NODE) -> Any:
        # handle acr
        if isinstance(node, Scope):
            previous_scope = self.scope
            self.scope = node

            previous_block = self.block
            self.block = node

            result = self.generic_visit(node)

            self.scope = previous_scope
            self.block = previous_block
        elif isinstance(node, Block):
            previous_block = self.block
            self.block = node

            result = self.generic_visit(node)

            self.block = previous_block
        else:
            result = self.generic_visit(node)

        return result

    def visit(self, node: NODE) -> Any:
        method = 'visit_' + type(node).__name__
        visitor = getattr(self, method, None)

        if visitor is None:
            # if self.strict:
            #     raise ValueError(
            #         f"There are no '{method}' method. "
            #         "You see this message because you're in strict mode. "
            #         f"See {type(self).__name__}.strict")

            if isinstance(node, ScopeReference):
                return self.generic_visit(node)

        # if not self.auto_global_visit:
        #     return visitor(node)

        if visitor is not None:
            result = visitor(node)
            self._acr_generic_visit(node)
        else:
            result = self._acr_generic_visit(node)

        return result

    def generic_visit(self, node: NODE) -> Any:
        if isinstance(node, ScopeReference):
            return self.visit(node.get_scope(self.scope))

        if isinstance(node, ast.AST):
            return self._ast_visitor.generic_visit(self, node)

        if isinstance(node, Block):
            for name in node._block_fields:
                container: FlowContainer = getattr(node, name)
                for item in container:
                    self.visit(item)
            return node

        if isinstance(node, CodeBlock):
            for code in node:
                self.visit(code)
            return node

        raise RuntimeError(
            f"Expected ACR or AST, but got {type(node).__name__}")


class ACRCodeTransformer(NodeVisitor):
    """Allows to change contents of the code (of the CodeBlock)"""

    _ast_visitor = ast.NodeTransformer

    def generic_visit(self, node: NODE) -> Any:
        if isinstance(node, ScopeReference):
            return self.visit(node.get_scope(self.scope))

        if isinstance(node, ast.AST):
            return self._ast_visitor.generic_visit(self, node)

        if isinstance(node, Block):
            for name in node._block_fields:
                container: FlowContainer = getattr(node, name)
                for i, item in enumerate(container):
                    container[i] = self.visit(item)
            return node

        if isinstance(node, CodeBlock):
            new_code_block: CodeBlock = CodeBlock()
            for code in node:
                value = self.visit(code)
                if value is None:
                    pass
                elif isinstance(value, (ast.AST, ACR)):
                    new_code_block.append(value)
                else:
                    new_code_block.extend(value)
            return node

        raise RuntimeError(
            f"Expected ACR or AST, but got {type(node).__name__}")
