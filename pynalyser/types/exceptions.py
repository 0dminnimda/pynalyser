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

    # unop
    "invert": "~",
    "pos": "+",
    "neg": "-"
}


def unsupported_op(op: str, lhs: str, rhs: str) -> TypeError:
    return TypeError(
        f"unsupported operand type(s) for {OP_TO_STR[op]}: '{lhs}' and '{rhs}'"
    )


def not_subscriptable(type: str) -> TypeError:
    return TypeError(f"'{type}' object is not subscriptable")


def bad_unary(op: str, type: str) -> TypeError:
    return TypeError(f"bad operand type for unary {OP_TO_STR[op]}: '{type}'")
