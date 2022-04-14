### Binary operation
BINOP_STR = {
    "Add": "+",
    "Sub": "-",
    "MatMult": "@",
    "Mult": "*",
    "Div": "/",
    "Mod": "%",
    "LShift": "<<",
    "RShift": ">>",
    "BitOr": "|",
    "BitXor": "^",
    "BitAnd": "&",
    "FloorDiv": "//",
    "Pow": "**"
}

BINOP_FUNC = {
    name: eval(f"lambda a, b: a {op} b")
    for name, op in BINOP_STR.items()}

DUNDER_BINOP = {
    "Add": "add",
    "Sub": "sub",
    "MatMult": "matmul",
    "Mult": "mul",
    "Div": "truediv",
    "Mod": "mod",
    "LShift": "lshift",
    "RShift": "rshift",
    "BitOr": "or",
    "BitXor": "xor",
    "BitAnd": "and",
    "FloorDiv": "floordiv",
    "Pow": "pow"
}


### Boolean operation
BOOLOP_STR = {
    "And": "and",
    "Or": "or"
}

# not need for BOOLOP_FUNC

# nothing is included
DUNDER_BOOLOP = {}


### Unary operation
UNOP_STR = {
    "Invert": "~",
    "Not": "not",
    "UAdd": "+",
    "USub": "-"
}

# not need for UNOP_FUNC

# Not is not included
DUNDER_UNOP = {
    "Invert": "invert",
    "UAdd": "pos",
    "USub": "neg"
}


### Compare operation
CMP_STR = {
    "Eq": "==",
    "NotEq": "!=",
    "Lt": "<",
    "LtE": "<=",
    "Gt": ">",
    "GtE": ">=",
    "Is": "is",
    "IsNot": "is not",
    "In": "in",
    "NotIn": "not in"
}

CMP_FUNC = {
    name: eval(f"lambda a, b: a {op} b")
    for name, op in CMP_STR.items()}

# Is, IsNot and NotIn are not included
DUNDER_CMP = {
    "Eq": "eq",
    "NotEq": "ne",
    "Lt": "lt",
    "LtE": "le",
    "Gt": "gt",
    "GtE": "ge",
    "In": "contains",
}
