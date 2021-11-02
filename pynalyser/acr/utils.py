import ast
from .classes import ACR
from typing import Any, List, NamedTuple, Optional, Union, Tuple, Collection
from collections import defaultdict


# @attr.s(auto_attribs=True, on_setattr=attr.setters.frozen)
class Context(NamedTuple):
    annotate_fields: bool
    include_attributes: bool
    indent: Optional[str]
    # lvl: int = attr.ib(on_setattr=attr.setters.NO_OP)


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
    # if isinstance(obj, list):
    #     if not obj:
    #         return "[]", True
    #     return (f"[{prefix}" +
    #             f"{sep.join(_format(x, ctx, lvl)[0] for x in obj)}]"), False

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

    # if isinstance(obj, dict):
    #     if not obj:
    #         return "{}", True
    #     args = sep.join(
    #         f"{_format(key, ctx, lvl)[0]}: {_format(value, ctx, lvl)[0]}"
    #         for key, value in obj.items())
    #     s = f"{{{prefix}{args}}}"
    #     if isinstance(obj, defaultdict):
    #         return f"defaultdict({obj.default_factory!r}, {s})", False
    #     return s, False
    if isinstance(obj, (ACR, ast.AST)):
        value, allsimple = _format_args_with_allsimple(
            prefix, sep, *_format_ast_or_acr(obj, ctx, lvl))
        return f"{type(obj).__name__}({value})", allsimple
        # return _format_class(
        #     obj, prefix, sep,)
    # if isinstance(obj, ast.AST):
    #     return _format_class(obj, prefix, sep, *_format_ast_or_acr(obj, ctx, lvl))

    return repr(obj), True


def _format_args_with_allsimple(prefix: str, sep: str, args: Collection[str],
                                allsimple: bool) -> Tuple[str, bool]:
    if allsimple and len(args) <= 3:
        return ", ".join(args), not args
    return prefix + sep.join(args), False


# def _format_class(obj: Any, prefix: str, sep: str, args: Collection[str],
#                   allsimple: bool) -> Tuple[str, bool]:
#     args, allsimple = _format_args_with_allsimple(prefix, sep, args, allsimple)
#     return f"{type(obj).__name__}({args})", allsimple

    # if allsimple and len(args) <= 3:
    #     return f"{type(inst).__name__}({", ".join(args)})", not args
    # return f"{type(inst).__name__}({prefix}{sep.join(args)})", False

    # C = TypeVar("C", bound=Callable[
    #     [Any, Context, int, str, str],
    #     Tuple[str, bool]])
    # P = ParamSpec("P")
    # R = Tuple[List[str], bool]

    # def wrap_class_function(f: Callable[P, R]) -> Callable[P, Tuple[str, bool]]:
    #     def wrapped(*args: P.args, **kwargs: P.kwargs) -> Tuple[str, bool]:
    #         args, allsimple = f(*args, **kwargs)
    #         if allsimple and len(args) <= 3:
    #             return f"{type(node).__name__}({', '.join(args)})", not args
    #         return f"{type(node).__name__}({prefix}{sep.join(args)})", False
    #     return wrapped

    # def is_default(cls: Type, name: str) -> bool:
    #     # XXX: is really needed?
    #     return False

    # T = TypeVar("T")
    # def add_logging(f: Callable[P, T]) -> Callable[P, T]:
    #     '''A type-safe decorator to add logging to a function.'''
    #     def inner(*args: P.args, **kwargs: P.kwargs) -> T:
    #         print(f'{f.__name__} was called')
    #         return f(*args, **kwargs)
    #     return inner


def _format_attr(inst: Any, name: str, ctx: Context,
                 lvl: int) -> Tuple[str, bool]:
    return _format(
        getattr(inst, name, "<Is not an attribute of the object>"), ctx, lvl)


# def _format_attrs(inst: Any, names: Iterable[str],
#                   ctx: Context, lvl: int) -> Iterable[Tuple[str, str, bool]]:
#     for name in names:
#         yield name, *_format_attr(inst, name, ctx, lvl)

    # yield name, *_format(
    #     getattr(inst, name, "<Is not an attribute of the object>"),
    #     ctx, lvl)


# def _format_ast(node: ast.AST, ctx: Context, lvl: int) -> Tuple[List[str], bool]:
#     # cls = type(node)
#     args = []
#     allsimple = True

#     # for name in names:
#     #     value, simple = _format(
#     #         getattr(node, name, "<Is not an attribute of the object>"), ctx)

#     # for name, value, simple in _format_attrs(node, node._fields, ctx, lvl):
#     #     allsimple = allsimple and simple
#     #     if ctx.annotate_fields:
#     #         # value = '(DEFAULT)' * is_default(cls, name) + value
#     #         args.append(f"{name}={value}")
#     #     else:
#     #         args.append(value)

#     for name in node._fields:
#         value, simple = _format_attr(node, name, ctx, lvl)
#         allsimple = allsimple and simple
#         if ctx.annotate_fields:
#             # value = '(DEFAULT)' * is_default(cls, name) + value
#             args.append(f"{name}={value}")
#         else:
#             args.append(value)

#     if ctx.include_attributes and node._attributes:
#         for name in node._attributes:
#             value, simple = _format_attr(node, name, ctx, lvl)
#             allsimple = allsimple and simple
#             args.append(f"{name}={value}")

#     return args, allsimple

    # if allsimple and len(args) <= 3:
    #     return f"{type(node).__name__}({', '.join(args)})", not args
    # return f"{type(node).__name__}({prefix}{sep.join(args)})", False

    # if isinstance(node, AST):
    # keywords = ctx.annotate_fields
    # for name in node._fields:
    #     try:
    #         value = getattr(node, name)
    #     except AttributeError:
    #         keywords = True
    #         continue
    #     if value is None and getattr(cls, name, ...) is None:
    #         keywords = True
    #         continue
    #     value, simple = _format(value, ctx)
    #     allsimple = allsimple and simple
    #     if keywords:
    #         args.append('%s=%s' % (name, value))
    #     else:
    #         args.append(value)
    # if include_attributes and node._attributes:
    #     for name in node._attributes:
    #         try:
    #             value = getattr(node, name)
    #         except AttributeError:
    #             continue
    #         if value is None and getattr(cls, name, ...) is None:
    #             continue
    #         value, simple = _format(value, ctx)
    #         allsimple = allsimple and simple
    #         args.append('%s=%s' % (name, value))
    # elif isinstance(node, list):
    #     if not node:
    #         return '[]', True
    #     return f"[{prefix}{sep.join(_format_ast(x, annotate_fields, include_attributes, indent, lvl)[0] for x in node)}]", False
    # return repr(node), True


# def dump_params(
#         params: Dict[str, Any], annotate_fields: bool,
#         include_attributes: bool, sep: str) -> str:
#     return sep.join(
#         (name + "=") * annotate_fields + dump(value, annotate_fields, include_attributes)
#         for name, value in params.items()
#     )


# CL = TypeVar("CL", ast.AST, ACR)


def _format_ast_or_acr(obj: Union[ast.AST, ACR], ctx: Context,
                       lvl: int) -> Tuple[List[str], bool]:
    args = []
    allsimple = True

    # for name, value, simple in _format_attrs(
    #         self, attr.fields_dict(type(self)).keys(), ctx, lvl):
    #     allsimple = allsimple and simple
    #     if ctx.annotate_fields:
    #         args.append(f"{name}={value}")
    #     else:
    #         args.append(value)

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


# @attr.s(auto_attribs=True)
# class AttrWithDump(ACR):
#     def _format(self, ctx: Context, lvl: int) -> Tuple[List[str], bool]:
#         args = []
#         allsimple = True

#         # for name, value, simple in _format_attrs(
#         #         self, attr.fields_dict(type(self)).keys(), ctx, lvl):
#         #     allsimple = allsimple and simple
#         #     if ctx.annotate_fields:
#         #         args.append(f"{name}={value}")
#         #     else:
#         #         args.append(value)

#         for name in self._fields:
#             value, simple = _format_attr(self, name, ctx, lvl)
#             allsimple = allsimple and simple
#             if ctx.annotate_fields:
#                 args.append(f"{name}={value}")
#             else:
#                 args.append(value)

#         if ctx.include_attributes and self._attributes:
#             for name in self._attributes:
#                 value, simple = _format_attr(self, name, ctx, lvl)
#                 allsimple = allsimple and simple
#                 args.append(f"{name}={value}")

#         return args, allsimple

#         # params = sep.join((name + "=") * annotate_fields +
#         #                   _format(value, annotate_fields, include_attributes)
#         #                   for name, value in params.items())

#         return (
#             type(self).__name__ + "(" +
#             dump_params(
#                 attr.asdict(self), annotate_fields,
#                 include_attributes, sep) +
#             ")")

#         # print(attr.asdict(self))
#         # print()
#         # print(attr.fields_dict(type(self)).keys())
#         # print()
#         # print(attr.fields(type(self)))

    # def dump(self, indent: Optional[int] = None, prev_indent: int = 0) -> str:
#        if indent is None:
#            sep = ""
#        else:
#            sep = "\n" + " "*(indent + prev_indent)
#        print(attr.fields_dict(type(self)).keys())
#        #print(attr.fields(type(self)))
#        return (
#            prev_indent*" " +
#            sep.join((
#                "Function(",
#                f"{self.name},",
#                ")"
#            ))
#        )


# ACR().dump()
