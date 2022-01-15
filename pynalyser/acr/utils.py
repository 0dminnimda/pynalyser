import ast
from collections import defaultdict
from typing import (Any, Collection, Iterator, List, NamedTuple, Optional,
                    Tuple, Union)

from .classes import ACR, Block, CodeBlock, Module, Scope, ScopeReference

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


NODE_TUP = (ACR, ast.AST)
NODE = Union[ACR, ast.AST]
FIELD = Union[List[NODE], NODE]

ACCEPTABLE_FIELD = (int, str, bool, defaultdict, type(None))
ACCEPTABLE_ITEM = CodeBlock


def do_nothing(*args, **kwargs):
    pass


def iter_fields(node: NODE) -> Iterator[Tuple[str, FIELD]]:
    for field in node._fields:
        try:
            yield field, getattr(node, field)
        except AttributeError:
            pass


class NodeVisitor:
    scope: Scope
    block: Block
    strict: bool = False

    def start(self, module: Module) -> None:
        self.scope = module
        self.block = module

        self.visit(module)

        del self.scope, self.block

    def visit(self, node: NODE) -> Any:
        method = 'visit_' + type(node).__name__
        visitor = getattr(self, method, None)

        if visitor is None:
            if self.strict:
                raise ValueError(
                    f"There are no '{method}' method. "
                    "You see this message because you're in strict mode. "
                    f"See {type(self).__name__}.strict")

            visitor = do_nothing

        # handle acr
        if isinstance(node, ScopeReference):
            scope = node.get_scope(self.scope)

            result = visitor(scope)

            previous_scope = self.scope
            previous_block = self.block

            self.scope = scope
            self.block = scope

            self.generic_visit(scope)

            self.scope = previous_scope
            self.block = previous_block
        elif isinstance(node, Block):
            result = visitor(node)

            previous_block = self.block
            self.block = node

            self.generic_visit(node)

            self.block = previous_block
        else:
            result = visitor(node)

            self.generic_visit(node)

        return result

    def generic_visit(self, node: NODE) -> Any:
        for field, value in iter_fields(node):
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, NODE_TUP):
                        self.visit(item)
                    elif isinstance(item, ACCEPTABLE_ITEM):
                        pass
                    else:
                        # XXX: is this nessesary?
                        raise TypeError(
                            "Expected node list item to be instance of "
                            "ACR, AST or CodeBlock "
                            f"but found {type(value).__name__}")
            elif isinstance(value, NODE_TUP):
                self.visit(value)
            elif isinstance(value, ACCEPTABLE_FIELD):
                pass
            else:
                # XXX: is this nessesary?
                raise TypeError(
                    "Expected node field to be instance of ACR, AST, list, "
                    "int, str, bool, defaultdict or type(None) "
                    f"but found {type(value).__name__}")

