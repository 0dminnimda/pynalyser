OP_TO_STR = {
    # binop
    "add": "+",
    "sub": "-",
    "matmul": "@",
    "mul": "*",
    "truediv": "/",
    "mod": "%",
    "lshift": "<<",
    "rshift": ">>",
    "or": "|",
    "xor": "^",
    "and": "&",
    "floordiv": "//",
    "pow": "**",

    # cmpop
    "eq": "==",
    "ne": "!=",
    "lt": "<",
    "le": "<=",
    "gt": ">",
    "ge": ">=",
    "contains": "in",
}


def unsupported_op(op: str, lhs: str, rhs: str) -> TypeError:
    return TypeError(
        f"unsupported operand type(s) for {OP_TO_STR[op]!r}: {lhs!r} and {rhs!r}"
    )


def not_subscriptable(type: str) -> TypeError:
    return TypeError(f"{type!r} object is not subscriptable")
