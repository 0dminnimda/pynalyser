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
    "neg": "-",
}


def binary_not_supported(op: str, lhs: str, rhs: str) -> TypeError:
    return TypeError(
        f"unsupported operand type(s) for {OP_TO_STR[op]}: '{lhs}' and '{rhs}'"
    )


def compare_not_supported(op: str, lhs: str, rhs: str) -> TypeError:
    return TypeError(
        f"'{OP_TO_STR[op]}' not supported between instances of '{lhs}' and '{rhs}'"
    )


def unary_not_supported(op: str, type: str) -> TypeError:
    return TypeError(f"bad operand type for unary {OP_TO_STR[op]}: '{type}'")


def not_iterable(type: str) -> TypeError:
    return TypeError(f"argument of type '{type}' is not iterable")


def not_subscriptable(type: str) -> TypeError:
    return TypeError(f"'{type}' object is not subscriptable")
